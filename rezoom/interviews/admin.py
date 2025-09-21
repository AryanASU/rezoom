from django.contrib import admin
from .models import EmployeeAvailability, Interview, InterviewInterviewer

@admin.register(EmployeeAvailability)
class EmployeeAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("employee","start","end","is_bookable")
    list_filter  = ("employee__company","is_bookable")
    date_hierarchy = "start"
    search_fields = ("employee__user__username","employee__user__email")

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("id","application","mode","status","start","end","location")
    list_filter  = ("status","mode","application__job__company")
    date_hierarchy = "start"
    readonly_fields = ("created_at","updated_at","invite_sent_at")
    fieldsets = (
        ("Link", {"fields": ("application",)}),
        ("Scheduling", {"fields": ("mode","status","start","end")}),
        ("Location", {"fields": ("location","location_text")}),
        ("Online (Zoom)", {"fields": ("zoom_meeting_id","zoom_join_url","zoom_start_url")}),
        ("Comms", {"fields": ("invite_sent_at","reminder_48h_sent","reminder_24h_sent")}),
        ("Artifacts", {"fields": ("notes_md","recording_file","transcript_text")}),
        ("System", {"fields": ("created_at","updated_at")}),
    )

@admin.register(InterviewInterviewer)
class InterviewInterviewerAdmin(admin.ModelAdmin):
    list_display = ("interview","employee","role")
    list_filter  = ("employee__company",)
    search_fields = ("employee__user__username","employee__user__email","interview__application__user__username")
