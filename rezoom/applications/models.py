from django.db import models
from django.utils import timezone
from accounts.models import User
from jobs.models import Job
from companies.models import Employee

class Application(models.Model):
    class Stage(models.TextChoices):
        SUBMITTED           = "submitted", "submitted"
        ATS_SCREEN          = "ats_screen", "ats_screen"
        EMPLOYEE_REVIEW     = "employee_review", "employee_review"
        INTERVIEW_PENDING   = "interview_pending", "interview_pending"      # candidate to schedule
        INTERVIEW_SCHEDULED = "interview_scheduled", "interview_scheduled"
        UNDER_CONSIDERATION = "under_consideration", "under_consideration"
        REJECTED            = "rejected", "rejected"
        OFFER               = "offer", "offer"
        HIRED               = "hired", "hired"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")

    # optional: store the resume used at apply time (even if profile resume later changes)
    resume_file = models.FileField(upload_to="resumes/apps/", blank=True, null=True)

    # optional: keep a frozen snapshot of key profile fields at apply time
    profile_snapshot = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=32, choices=Stage.choices, default=Stage.SUBMITTED)
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    ats_score   = models.PositiveSmallIntegerField(default=0)
    ats_outcome = models.CharField(
            max_length=20,
            choices=[("pass","Pass"), ("below","Below threshold")],
            default="below",
        )
    ats_summary = models.JSONField(default=dict, blank=True)
    
    class Meta:
        unique_together = ("job", "user")  # prevent duplicate applies
        indexes = [
            models.Index(fields=["job", "status"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.job.title} [{self.status}]"


class ApplicationScore(models.Model):
    """ATS score + transparent reasons used to route (>= threshold → employee_review)."""
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="score")
    ats_score = models.IntegerField(default=0)                 # 0–100
    reasons = models.JSONField(default=dict, blank=True)       # e.g. {"matched_skills":[...],"missing_skills":[...]}
    model_version = models.CharField(max_length=32, default="v1")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ATS {self.ats_score} for app {self.application_id}"


class ApplicationAssignment(models.Model):
    """
    Distributes an application to Employee reviewers (those who accepted the job assignment).
    """
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="assignments")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="application_assignments")

    is_owner = models.BooleanField(default=False)              # mark a primary reviewer if needed
    decision = models.CharField(max_length=12, blank=True)     # "", "approve", "reject"
    decision_notes = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("application", "employee")
        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["application"]),
        ]

    def __str__(self):
        who = self.employee.user.get_full_name() or self.employee.user.username
        return f"{who} reviewing app {self.application_id}"
