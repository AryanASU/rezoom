from django.db import models
from django.utils import timezone
from companies.models import Employee, OfficeLocation
from applications.models import Application

class EmployeeAvailability(models.Model):
    """
    Employee sets next 3 weeks availability; candidate picks from these 1h slots.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="availability")
    start = models.DateTimeField()
    end = models.DateTimeField()
    is_bookable = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["employee","start"]), models.Index(fields=["is_bookable"])]

    def __str__(self):
        return f"{self.employee} · {self.start:%Y-%m-%d %H:%M} → {self.end:%H:%M}"


class Interview(models.Model):
    class Mode(models.TextChoices):
        ONLINE = "online", "Online"
        INPERSON = "inperson", "In person"

    class Status(models.TextChoices):
        PENDING_EMP_APPROVAL = "pending_emp_approval", "Pending EMP approval"  # candidate picked; waiting EMP
        AWAITING_CANDIDATE  = "awaiting_candidate", "Awaiting candidate"       # invite sent; waiting pick
        AWAITING_EMP_CONFIRM= "awaiting_emp_confirm", "Awaiting EMP confirm"   # candidate picked; need confirm
        CONFIRMED           = "confirmed", "Confirmed"
        COMPLETED           = "completed", "Completed"
        CANCELLED           = "cancelled", "Cancelled"

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="interviews")
    mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.ONLINE)

    # Scheduling
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.AWAITING_CANDIDATE)

    # In-person location (optional)
    location = models.ForeignKey(OfficeLocation, on_delete=models.SET_NULL, null=True, blank=True)
    location_text = models.CharField(max_length=255, blank=True)  # free-text override (room, notes)

    # Online (Zoom) placeholders — we will generate after EMP confirm
    zoom_meeting_id = models.CharField(max_length=128, blank=True)
    zoom_join_url = models.URLField(blank=True)
    zoom_start_url = models.URLField(blank=True)  # host link (employee)

    # Communications & reminders
    invite_sent_at = models.DateTimeField(null=True, blank=True)  # link to schedule
    reminder_48h_sent = models.BooleanField(default=False)
    reminder_24h_sent = models.BooleanField(default=False)

    # Artifacts
    notes_md = models.TextField(blank=True)
    recording_file = models.FileField(upload_to="interview_recordings/", blank=True, null=True)
    transcript_text = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["application","status"]),
            models.Index(fields=["start"]),
        ]

    def __str__(self):
        return f"Interview #{self.id} · {self.application.user.username} × {self.application.job.title}"


class InterviewInterviewer(models.Model):
    """Who will interview? (allow 1..n interviewers)"""
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name="interviewers")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="interviews_as_interviewer")
    role = models.CharField(max_length=64, blank=True, help_text="e.g., Panelist, Lead, HR")

    class Meta:
        unique_together = ("interview","employee")

    def __str__(self):
        return f"{self.employee} on {self.interview_id}"
