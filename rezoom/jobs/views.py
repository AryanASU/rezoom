from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from .forms import JobForm
from .models import Job, JobAssignee
from companies.models import Company, Employee

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from applications.models import Application
from .models import Job
from companies.models import Company
from accounts.models import UserProfile


def hr_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "HR":
            return HttpResponseForbidden("HR access only")
        return view(request, *args, **kwargs)
    return wrapper

@login_required
@hr_required
def job_create(request):
    if request.method == "POST":
        form = JobForm(request.POST, user=request.user)
        if form.is_valid():
            job = form.save()
            # Build assignees
            assignee_ids = form._assignees_ids
            if assignee_ids:
                qs = Employee.objects.filter(company=job.company, id__in=assignee_ids)
                for emp in qs:
                    JobAssignee.objects.get_or_create(job=job, employee=emp)
            messages.success(request, "Job posted.")
            return redirect("job_detail", pk=job.pk)
    else:
        form = JobForm(user=request.user)
    # pre-populate employee choices for the first company (if any)
    companies = Company.objects.filter(created_by=request.user)
    first_company = companies.first()
    employees = Employee.objects.filter(company=first_company) if first_company else Employee.objects.none()
    form.fields["assignees"].choices = [(e.id, f"{e.user.get_full_name() or e.user.username} · {e.job_role}") for e in employees]
    return render(request, "jobs/job_create.html", {"form": form, "companies": companies})

@login_required
@hr_required
def employees_json(request, company_id):
    emps = Employee.objects.filter(company_id=company_id).select_related("user").order_by("user__username")
    data = [{"id": e.id, "label": f"{e.user.get_full_name() or e.user.username} · {e.job_role}"} for e in emps]
    return JsonResponse({"employees": data})

@login_required
@hr_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, company__created_by=request.user)
    assignees = job.assignees.select_related("employee__user")
    return render(request, "jobs/job_detail.html", {"job": job, "assignees": assignees})

@login_required
def job_browse(request):
    qs = Job.objects.select_related("company").filter(status="open").order_by("-created_at")

    # --- filters ---
    q = request.GET.get("q", "").strip()
    mode = request.GET.get("mode", "").strip()          # onsite/remote/hybrid
    company_id = request.GET.get("company", "").strip()
    min_salary = request.GET.get("min", "").strip()
    use_profile = request.GET.get("profile", "") == "1"

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description_md__icontains=q) |
            Q(responsibilities_md__icontains=q) |
            Q(role_purpose__icontains=q)
        )
    if mode in {"onsite","remote","hybrid"}:
        qs = qs.filter(location_mode=mode)
    if company_id.isdigit():
        qs = qs.filter(company_id=int(company_id))
    if min_salary.isdigit():
        qs = qs.filter(salary_min__gte=int(min_salary))

    # simple "match" score using candidate skills vs job req_quals/tools
    matches = {}
    profile_skills = set()
    if use_profile and request.user.is_authenticated:
        try:
            profile_skills = set((request.user.profile.skills or []))
        except UserProfile.DoesNotExist:
            profile_skills = set()
    jobs = list(qs[:50])
    if profile_skills:
        for j in jobs:
            req = set((j.req_quals or []) + (j.tools or []))
            inter = len(req & profile_skills)
            denom = max(1, len(req))
            matches[j.id] = round(100 * inter / denom)

        # sort by match score desc if using profile
        jobs.sort(key=lambda j: matches.get(j.id, 0), reverse=True)

    companies = Company.objects.all().order_by("name")
    return render(request, "jobs/browse.html", {
        "jobs": jobs,
        "companies": companies,
        "matches": matches,
        "params": {"q": q, "mode": mode, "company": company_id, "min": min_salary, "profile": use_profile},
    })

@login_required
def job_public_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related("company"), pk=pk, status="open")
    return render(request, "jobs/job_public_detail.html", {"job": job})


@login_required
def assignee_response(request, pk):
    # only the assigned employee can respond
    ja = get_object_or_404(JobAssignee, pk=pk, employee__user=request.user)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "accept":
            ja.status = JobAssignee.InviteStatus.ACCEPTED
            ja.save()
            messages.success(request, "Invite accepted. You can now review applications for this job.")
        elif action == "decline":
            ja.status = JobAssignee.InviteStatus.DECLINED
            ja.save()
            messages.info(request, "Invite declined.")
    return redirect("emp_dashboard")

@login_required
@hr_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, company__created_by=request.user)
    assignees = job.assignees.select_related("employee__user")

    stats = {
        "apps_total": Application.objects.filter(job=job).count(),
        "ats_pass": Application.objects.filter(job=job, ats_outcome="pass").count(),
        "ats_below": Application.objects.filter(job=job, ats_outcome="below").count(),
    }
    return render(request, "jobs/job_detail.html", {"job": job, "assignees": assignees, "stats": stats})