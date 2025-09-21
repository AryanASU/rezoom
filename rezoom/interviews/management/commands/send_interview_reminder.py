from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.utils import notify
from interviews.models import Interview

class Command(BaseCommand):
    help = "Send 48h and 24h interview reminders (candidate + interviewer)."

    def handle(self, *args, **opts):
        now = timezone.now()

        def window(hours):
            start = now + timezone.timedelta(hours=hours) - timezone.timedelta(minutes=30)
            end   = now + timezone.timedelta(hours=hours) + timezone.timedelta(minutes=30)
            return start, end

        # 48h window
        s48, e48 = window(48)
        q48 = Interview.objects.select_related("application__user","application__job__company")\
            .filter(status="confirmed", start__gte=s48, start__lte=e48, reminder_48h_sent=False)

        for iv in q48:
            cand = iv.application.user
            msg = f"Reminder: your interview for {iv.application.job.title} on {iv.start:%b %d, %Y %I:%M %p}."
            notify(cand, "Interview in 48 hours", msg, send_email=True)
            for ii in iv.interviewers.select_related("employee__user"):
                notify(ii.employee.user, "Interview in 48 hours", msg, send_email=True)
            iv.reminder_48h_sent = True
            iv.save(update_fields=["reminder_48h_sent"])

        # 24h window
        s24, e24 = window(24)
        q24 = Interview.objects.select_related("application__user","application__job__company")\
            .filter(status="confirmed", start__gte=s24, start__lte=e24, reminder_24h_sent=False)

        for iv in q24:
            cand = iv.application.user
            msg = f"Reminder: your interview for {iv.application.job.title} is tomorrow at {iv.start:%I:%M %p}."
            notify(cand, "Interview in 24 hours", msg, send_email=True)
            for ii in iv.interviewers.select_related("employee__user"):
                notify(ii.employee.user, "Interview in 24 hours", msg, send_email=True)
            iv.reminder_24h_sent = True
            iv.save(update_fields=["reminder_24h_sent"])

        self.stdout.write(self.style.SUCCESS("Reminders complete."))
