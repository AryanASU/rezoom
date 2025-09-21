from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from .models import Notification

def notify(user, title, message="", url=None, send_email=True, email_subject=None):
    n = Notification.objects.create(
        user=user, title=title, message=message or "", url=url or ""
    )
    if send_email and getattr(settings, "EMAIL_BACKEND", ""):
        subj = email_subject or title
        body = message or title
        if url:
            body += f"\n\nOpen: {url}"
        send_mail(subj, body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
        n.email_sent = True
        n.save(update_fields=["email_sent"])
    return n
