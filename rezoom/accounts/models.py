from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "USER", "User"      # candidate
        HR   = "HR", "HR"          # company account (we’ll also add company logo in Step 2)
        EMP  = "EMP", "Employee"   # interviewer/reviewer
    role = models.CharField(max_length=8, choices=Role.choices, default=Role.USER)
    google_sub = models.CharField(max_length=128, blank=True, null=True, unique=True)  # for OAuth later

    def __str__(self):
        return f"{self.username} ({self.role})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # NEW: profile photo
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    # Demographics
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=32, blank=True)
    address = models.TextField(blank=True)

    # Structured data
    education = models.JSONField(default=list, blank=True)          # [{degree, school, year, grade}]
    skills = models.JSONField(default=list, blank=True)             # ["Django","GSAP","Lenis",...]
    experience = models.JSONField(default=list, blank=True)         # [{company, title, start, end, years, desc}]
    projects = models.JSONField(default=list, blank=True)           # [{title, technologies:[...], github}]
    interests = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)     # [{name, issuer, year}]
    languages = models.JSONField(default=list, blank=True)

    # Singles
    contract_type = models.CharField(max_length=64, blank=True)     # Full-time / Contract, etc.
    visa_status = models.CharField(max_length=64, blank=True)       # Needs Sponsorship / No
    github_url = models.URLField(blank=True)

    # Files
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    # housekeeping
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile<{self.user_id}>"

# auto-create a blank profile for every new user
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
