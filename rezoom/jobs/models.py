from django.db import models
from django.utils import timezone
from companies.models import Company, Employee
from accounts.models import User

class Job(models.Model):
    class Mode(models.TextChoices):
        ONSITE = "onsite", "On-site"
        REMOTE = "remote", "Remote"
        HYBRID = "hybrid", "Hybrid"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        PAUSED = "paused", "Paused"

    # --- Basic Information ---
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=200)                               # role name
    department = models.CharField(max_length=150, blank=True)              # team/department
    manager = models.ForeignKey(                                           
        User, on_delete=models.SET_NULL, null=True, blank=True,            # reports to (optional FK)
        related_name="manages_jobs"
    )
    manager_name = models.CharField(max_length=150, blank=True)            # fallback display
    emp_type = models.CharField(max_length=50, blank=True)                 # full-time/contract/internship
    location_mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.HYBRID)
    location_text = models.CharField(max_length=255, blank=True)
    deadline = models.DateField(null=True, blank=True)

    # --- Role Purpose / Description / Responsibilities ---
    role_purpose = models.TextField(blank=True)
    description_md = models.TextField(blank=True)
    responsibilities_md = models.TextField(blank=True)

    # --- Qualifications (checkbox-like in UI, flexible here) ---
    req_quals = models.JSONField(default=list, blank=True)  # e.g. ["3+ years Django","PostgreSQL","React"]
    pref_quals = models.JSONField(default=list, blank=True)
    perf_metrics = models.JSONField(default=list, blank=True)  # how success is measured

    # --- Compensation & Benefits ---
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, blank=True, default="USD")
    pay_period = models.CharField(max_length=16, blank=True, default="year")  # year/month/hour
    benefits = models.JSONField(default=list, blank=True)  # pick-list in UI, stored as list of strings

    # --- Work Environment ---
    team_size = models.PositiveIntegerField(null=True, blank=True)
    tools = models.JSONField(default=list, blank=True)  # ["Django","Docker","Jira"]

    # --- Legal & Compliance ---
    visa_sponsorship = models.BooleanField(default=False)
    background_check_required = models.BooleanField(default=False)
    security_clearance = models.CharField(max_length=64, blank=True)
    eeo_text = models.TextField(blank=True)

    # --- Status & Timestamps ---
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["title"]),
            models.Index(fields=["deadline"]),
        ]

    def __str__(self):
        return f"{self.title} · {self.company.name}"


class JobAssignee(models.Model):
    """
    Many-to-many link between a Job and the Employee(s) assigned to handle applications/interviews.
    Allows invite/accept/decline workflow.
    """
    class InviteStatus(models.TextChoices):
        INVITED = "invited", "Invited"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="assignees")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="assignments")
    status = models.CharField(max_length=12, choices=InviteStatus.choices, default=InviteStatus.INVITED)

    # Optional: priority or share of workload
    priority = models.PositiveIntegerField(default=0)  # 0 = normal; higher = earlier in queue

    class Meta:
        unique_together = ("job", "employee")

    def __str__(self):
        return f"{self.employee} → {self.job} ({self.status})"
