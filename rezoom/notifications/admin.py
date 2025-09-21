from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user","title","is_read","created_at","email_sent","url")
    list_filter = ("is_read","email_sent")
    search_fields = ("user__username","title","message","url")
