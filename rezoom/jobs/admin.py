from django.contrib import admin
from .models import Job, JobAssignee

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title","company","status","location_mode","emp_type","deadline","created_at")
    list_filter  = ("company","status","location_mode","emp_type")
    search_fields = ("title","department","manager_name","description_md","responsibilities_md")
    date_hierarchy = "created_at"
    fieldsets = (
        ("Basics", {
            "fields": ("company","title","department","manager","manager_name","emp_type",
                       "location_mode","location_text","deadline","status")
        }),
        ("Role Content", {
            "fields": ("role_purpose","description_md","responsibilities_md")
        }),
        ("Qualifications", {
            "fields": ("req_quals","pref_quals","perf_metrics")
        }),
        ("Compensation & Benefits", {
            "fields": ("salary_min","salary_max","currency","pay_period","benefits")
        }),
        ("Work Environment", {
            "fields": ("team_size","tools")
        }),
        ("Legal & Compliance", {
            "fields": ("visa_sponsorship","background_check_required","security_clearance","eeo_text")
        }),
        ("Timestamps", {
            "fields": ("created_at","updated_at"),
        }),
    )
    readonly_fields = ("created_at","updated_at")

@admin.register(JobAssignee)
class JobAssigneeAdmin(admin.ModelAdmin):
    list_display = ("job","employee","status","priority")
    list_filter  = ("status","job__company")
    search_fields = ("job__title","employee__user__username","employee__user__email")
