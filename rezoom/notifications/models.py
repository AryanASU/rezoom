from django.db import models
from django.utils import timezone
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=140)
    message = models.TextField(blank=True)
    url = models.CharField(max_length=255, blank=True)  # internal link like /u/ or /jobs/1/
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user","is_read","created_at"])]

    def __str__(self):
        return f"{self.user} · {self.title}"
