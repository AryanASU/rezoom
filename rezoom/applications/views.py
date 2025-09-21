from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from notifications.utils import notify
from .models import Application
from .forms import ApplyForm
from jobs.models import Job
from .ats import score_profile_against_job

@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id, status="open")
    # Optional: restrict to candidate role
    if request.user.role not in ("USER",) and not request.user.is_superuser:
        messages.error(request, "Only candidates can apply.")
        return redirect("job_public_detail", pk=job.id)

    existing = Application.objects.filter(job=job, user=request.user).first()
    if existing:
        messages.info(request, "You already applied to this job.")
        return redirect("job_public_detail", pk=job.id)

    if request.method == "POST":
        form = ApplyForm(request.POST, request.FILES)
        if form.is_valid():
            app = Application.objects.create(
                job=job,
                user=request.user,
                status=Application.Stage.SUBMITTED,
                created_at=timezone.now(),
                profile_snapshot={
                    "skills": request.user.profile.skills,
                    "education": request.user.profile.education,
                    "experience": request.user.profile.experience,
                    "projects": request.user.profile.projects,
                    "contract_type": request.user.profile.contract_type,
                    "visa_status": request.user.profile.visa_status,
                    "github_url": request.user.profile.github_url,
                },
            )
            # attach uploaded resume or fall back to profile resume
            up = form.cleaned_data.get("resume_file")
            if up:
                app.resume_file = up
            elif request.user.profile.resume:
                # reuse the candidate's saved resume file
                app.resume_file = request.user.profile.resume
            app.save()

            notify(
                request.user,
                title="Application submitted",
                message=f"You applied to {job.title} at {job.company.name}.",
                url=reverse("job_public_detail", args=[job.id]),
                send_email=True,
            )

            messages.success(request, "Application submitted.")
            return redirect("user_dashboard")
    else:
        form = ApplyForm()

    return render(request, "applications/apply.html", {"job": job, "form": form})

from django.db.models import Q

from .models import Application, ApplicationAssignment
from .forms import ReviewDecisionForm
from jobs.models import JobAssignee

@login_required
def employee_queue(request):
    # applications already assigned to this employee
    queue = (
        ApplicationAssignment.objects
        .select_related("application__job__company", "application__user")
        .filter(employee__user=request.user, decision="")
        .order_by("application__created_at")
    )
    return render(request, "applications/queue.html", {"queue": queue})

@login_required
def queue_decide(request, aa_id):
    aa = get_object_or_404(
        ApplicationAssignment.objects.select_related("application__job__company"),
        id=aa_id, employee__user=request.user
    )
    if request.method == "POST":
        form = ReviewDecisionForm(request.POST)
        if form.is_valid():
            dec = form.cleaned_data["decision"]
            aa.decision = dec
            aa.decision_notes = form.cleaned_data["notes"]
            aa.decided_at = timezone.now()
            aa.save()

            # advance application status on approve
            app = aa.application
            if dec == "approve":
                if app.status in (Application.Stage.SUBMITTED, Application.Stage.ATS_SCREEN, Application.Stage.EMPLOYEE_REVIEW):
                    app.status = Application.Stage.INTERVIEW_PENDING  # next step: candidate schedules
                    app.save()
                messages.success(request, "Approved — candidate can be invited to schedule.")
            else:
                app.status = Application.Stage.REJECTED
                app.rejection_reason = aa.decision_notes or "Rejected by reviewer."
                app.save()

                candidate = app.user

                if dec == "approve":
                    notify(
                        candidate,
                        title="Approved for interview",
                        message=f"You're approved to schedule an interview for {app.job.title} at {app.job.company.name}.",
                        url=reverse("schedule_invite", args=[app.id]),
                        send_email=True,
                    )
                else:
                    notify(
                        candidate,
                        title="Application update",
                        message=f"Your application for {app.job.title} at {app.job.company.name} was not selected.",
                        url=reverse("job_public_detail", args=[app.job.id]),
                        send_email=True,
                    )
                messages.info(request, "Rejected and candidate will see the status.")

            return redirect("employee_queue")
    else:
        form = ReviewDecisionForm()

    return render(request, "applications/decide.html", {"aa": aa, "form": form})

@login_required
def build_queue(request):
    """
    Auto-create ApplicationAssignment rows for jobs where this EMP is an ACCEPTED assignee.
    Pull unassigned applications in Submitted/Employee Review status.
    """
    # find jobs this employee accepted
    accepted = JobAssignee.objects.select_related("job").filter(
        employee__user=request.user, status="accepted"
    ).values_list("job_id", flat=True)

    # pull apps not yet assigned to this employee
    apps = (
        Application.objects
        .filter(job_id__in=accepted, status__in=["submitted","employee_review"])
        .exclude(assignments__employee__user=request.user)
        .order_by("created_at")[:20]  # cap to avoid flooding
    )

    from companies.models import Employee
    emp = Employee.objects.get(user=request.user)

    created = 0
    for app in apps:
        ApplicationAssignment.objects.get_or_create(application=app, employee=emp)
        # put app into employee_review if still submitted
        if app.status == Application.Stage.SUBMITTED:
            app.status = Application.Stage.EMPLOYEE_REVIEW
            app.save()
        created += 1

    if created:
        messages.success(request, f"Added {created} applications to your queue.")
    else:
        messages.info(request, "No new applications available.")
    return redirect("employee_queue")

ATS_THRESHOLD = 70  # feel free to tweak or move to settings


def apply_to_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id, status="open")

    if request.user.role not in ("USER",) and not request.user.is_superuser:
        messages.error(request, "Only candidates can apply.")
        return redirect("job_public_detail", pk=job.id)

    existing = Application.objects.filter(job=job, user=request.user).first()
    if existing:
        messages.info(request, "You already applied to this job.")
        return redirect("job_public_detail", pk=job.id)

    if request.method == "POST":
        form = ApplyForm(request.POST, request.FILES)
        if form.is_valid():
            # build the application
            app = Application.objects.create(
                job=job,
                user=request.user,
                status=Application.Stage.SUBMITTED,
                created_at=timezone.now(),
                profile_snapshot={
                    "skills": request.user.profile.skills,
                    "education": request.user.profile.education,
                    "experience": request.user.profile.experience,
                    "projects": request.user.profile.projects,
                    "contract_type": request.user.profile.contract_type,
                    "visa_status": request.user.profile.visa_status,
                    "github_url": request.user.profile.github_url,
                },
            )
            up = form.cleaned_data.get("resume_file")
            if up:
                app.resume_file = up
            elif request.user.profile.resume:
                app.resume_file = request.user.profile.resume

            # --- ATS scoring ---
            score, summary = score_profile_against_job(request.user.profile, job)
            app.ats_score = score
            app.ats_summary = summary
            if score >= ATS_THRESHOLD:
                app.ats_outcome = "pass"
                app.status = Application.Stage.EMPLOYEE_REVIEW  # ready for EMP queue
                notify(
                    request.user,
                    title="Passed ATS",
                    message=f"You passed initial screening for {job.title} at {job.company.name}.",
                    url=reverse("job_public_detail", args=[job.id]),
                    send_email=True,
                )
            else:
                app.ats_outcome = "below"
                app.status = Application.Stage.REJECTED
                app.rejection_reason = "ATS screening below threshold."
                notify(
                    request.user,
                    title="Application update",
                    message=f"Your application for {job.title} at {job.company.name} did not pass initial screening.",
                    url=reverse("job_public_detail", args=[job.id]),
                    send_email=True,
                )

            app.save()

            messages.success(request, "Application submitted.")
            return redirect("user_dashboard")
    else:
        form = ApplyForm()

    return render(request, "applications/apply.html", {"job": job, "form": form})