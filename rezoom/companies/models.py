from django.db import models
from django.utils import timezone
from accounts.models import User

class Company(models.Model):
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=200, blank=True)    # e.g., example.com
    address = models.TextField(blank=True)

    # NEW: company logo
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="companies_created"
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [models.Index(fields=["name"])]

    def __str__(self) -> str:
        return self.name


class Employee(models.Model):
    """
    Links a User (role=EMP) to a Company. These are reviewers/interviewers.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "EMP"}
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")
    job_role = models.CharField(max_length=150)           # e.g., Senior Engineer
    years_exp = models.FloatField(default=0)              # total years exp
    is_active = models.BooleanField(default=True)

    # NEW: employee photo
    photo = models.ImageField(upload_to="employee_photos/", blank=True, null=True)

    class Meta:
        unique_together = ("user", "company")
        indexes = [models.Index(fields=["company", "is_active"])]

    def __str__(self) -> str:
        who = self.user.get_full_name() or self.user.username
        return f"{who} @ {self.company.name}"

class OfficeLocation(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="locations")
    label = models.CharField(max_length=120, help_text="e.g., HQ – Floor 5")
    address = models.TextField(blank=True)
    room = models.CharField(max_length=64, blank=True, help_text="e.g., Room 5A")
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("company", "label", "room")
        indexes = [models.Index(fields=["company","label"])]

    def __str__(self) -> str:
        base = self.label
        if self.room: base += f" ({self.room})"
        return f"{self.company.name} · {base}"
