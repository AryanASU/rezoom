from django.contrib import admin
from .models import Application, ApplicationScore, ApplicationAssignment

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id","job","user","status","created_at")
    list_filter  = ("status","job__company")
    search_fields = ("user__username","user__email","job__title")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at","updated_at")

@admin.register(ApplicationScore)
class ApplicationScoreAdmin(admin.ModelAdmin):
    list_display = ("application","ats_score","model_version","updated_at")
    list_filter  = ("model_version",)
    search_fields = ("application__user__username","application__job__title")
    readonly_fields = ("created_at","updated_at")

@admin.register(ApplicationAssignment)
class ApplicationAssignmentAdmin(admin.ModelAdmin):
    list_display = ("application","employee","is_owner","decision","decided_at")
    list_filter  = ("decision","employee__company")
    search_fields = ("application__job__title","employee__user__username","employee__user__email")
