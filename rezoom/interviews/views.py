from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
import time
from notifications.utils import notify
from django.urls import reverse
from companies.models import Employee, OfficeLocation
from jobs.models import JobAssignee
from applications.models import Application
from .models import EmployeeAvailability, Interview, InterviewInterviewer
from .forms import AvailabilityForm, CandidateScheduleForm

@login_required
def availability_list(request):
    emp = Employee.objects.get(user=request.user)
    slots = (EmployeeAvailability.objects
             .filter(employee=emp)
             .order_by("start"))
    form = AvailabilityForm()
    return render(request, "interviews/availability.html", {"slots": slots, "form": form})

@login_required
def availability_add(request):
    emp = Employee.objects.get(user=request.user)
    if request.method == "POST":
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.employee = emp
            # quick guard: 60 min default if end missing (shouldn’t happen due to required fields)
            if not slot.end:
                slot.end = slot.start + timezone.timedelta(hours=1)
            slot.save()
            messages.success(request, "Availability added.")
    return redirect("availability_list")

@login_required
def availability_delete(request, slot_id):
    emp = Employee.objects.get(user=request.user)
    EmployeeAvailability.objects.filter(id=slot_id, employee=emp).delete()
    messages.info(request, "Availability removed.")
    return redirect("availability_list")

@login_required
def schedule_invite(request, app_id):
    """
    Candidate picks a 1-hour slot with an accepted assignee.
    Creates Interview(status=awaiting_emp_confirm). Marks slot unbookable.
    """
    app = get_object_or_404(
        Application.objects.select_related("job__company", "user"),
        id=app_id, user=request.user
    )
    if app.status != Application.Stage.INTERVIEW_PENDING:
        messages.info(request, "This application is not ready for scheduling yet.")
        return redirect("user_dashboard")

    # employees who ACCEPTED for this job
    accepted_emps = Employee.objects.filter(
        assignments__job=app.job, assignments__status="accepted"
    )
    # bookable future slots (next 21 days)
    now = timezone.now()
    until = now + timezone.timedelta(days=21)
    slots = (EmployeeAvailability.objects
             .select_related("employee__user")
             .filter(employee__in=accepted_emps, is_bookable=True, start__gte=now, start__lte=until)
             .order_by("start"))

    form = CandidateScheduleForm()
    form.set_slot_choices(slots)
    form.set_location_qs(OfficeLocation.objects.filter(company=app.job.company))

    if request.method == "POST":
        form = CandidateScheduleForm(request.POST)
        form.set_slot_choices(slots)  # must set choices again on POST
        form.set_location_qs(OfficeLocation.objects.filter(company=app.job.company))
        if form.is_valid():
            slot_id = int(form.cleaned_data["slot"])
            mode = form.cleaned_data["mode"]
            loc = form.cleaned_data.get("location")
            loc_text = form.cleaned_data.get("location_text") or ""

            # re-check slot still available & belongs to accepted employees
            slot = EmployeeAvailability.objects.select_related("employee").filter(
                id=slot_id, is_bookable=True, employee__in=accepted_emps
            ).first()
            if not slot:
                messages.error(request, "That slot is no longer available. Pick another.")
                return redirect("schedule_invite", app_id=app.id)

            # create interview
            iv = Interview.objects.create(
                application=app,
                mode=mode,
                start=slot.start,
                end=slot.end,
                status=Interview.Status.AWAITING_EMP_CONFIRM,
                location=loc if mode == "inperson" else None,
                location_text=loc_text if mode == "inperson" else "",
                invite_sent_at=timezone.now(),
            )

            interviewer_user = slot.employee.user
            notify(
                interviewer_user,
                title="Interview to confirm",
                message=f"{app.user.username} requested {iv.start:%b %d, %Y %I:%M %p} for {app.job.title}.",
                url=reverse("pending_confirms"),
                send_email=True,
            )
            # interviewer is the owner of the slot
            InterviewInterviewer.objects.create(interview=iv, employee=slot.employee)

            # mark slot taken
            slot.is_bookable = False
            slot.save(update_fields=["is_bookable"])

            # advance application status
            app.status = Application.Stage.INTERVIEW_SCHEDULED
            app.save(update_fields=["status"])

            messages.success(request, "Interview requested! Waiting for interviewer to confirm.")
            return redirect("user_dashboard")

    return render(request, "interviews/schedule.html", {
        "app": app, "form": form, "slots": slots,
    })


@login_required
def pending_confirms(request):
    """
    EMP view: interviews awaiting my confirmation.
    """
    emp = Employee.objects.filter(user=request.user).first()
    if not emp:
        messages.error(request, "You don't have an Employee profile yet.")
        return redirect("emp_dashboard")

    items = (Interview.objects
             .select_related("application__job__company", "application__user", "location")
             .filter(interviewers__employee=emp, status=Interview.Status.AWAITING_EMP_CONFIRM)
             .order_by("start"))
    return render(request, "interviews/pending.html", {"items": items})


@login_required
def confirm_interview(request, interview_id):
    """
    EMP confirms an interview; generate Zoom placeholders if online.
    """
    emp = Employee.objects.filter(user=request.user).first()
    if not emp:
        messages.error(request, "No Employee profile.")
        cand = iv.application.user
        extra = f" Join: {iv.zoom_join_url}" if iv.zoom_join_url else ""
        notify(
            cand,
            title="Interview confirmed",
            message=f"{iv.start:%b %d, %Y %I:%M %p} for {iv.application.job.title} is confirmed.{extra}",
            url=reverse("user_dashboard"),
            send_email=True,
        )
        return redirect("emp_dashboard")

    iv = get_object_or_404(
        Interview.objects.select_related("application__job__company"),
        id=interview_id, interviewers__employee=emp, status=Interview.Status.AWAITING_EMP_CONFIRM
    )

    if request.method == "POST":
        # generate simple placeholder values (actual Zoom integration later)
        if iv.mode == Interview.Mode.ONLINE and not iv.zoom_join_url:
            stamp = int(time.time())
            iv.zoom_meeting_id = f"rezoom-{iv.id}-{stamp}"
            iv.zoom_join_url  = f"https://zoom.example.com/join/{iv.zoom_meeting_id}"
            iv.zoom_start_url = f"https://zoom.example.com/host/{iv.zoom_meeting_id}"

        iv.status = Interview.Status.CONFIRMED
        iv.save(update_fields=["status", "zoom_meeting_id", "zoom_join_url", "zoom_start_url"])
        messages.success(request, "Interview confirmed.")
        return redirect("pending_confirms")

    # GET just shows a small confirm UI
    return render(request, "interviews/confirm.html", {"iv": iv})