from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Role & OAuth", {"fields": ("role","google_sub")}),
    )
    list_display = ("username","email","first_name","last_name","role","is_staff","is_active")
    list_filter = ("role","is_staff","is_active")
    search_fields = ("username","email","first_name","last_name")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user","github_url","visa_status","contract_type","updated_at")
    readonly_fields = ()
    fields = (
        "user","profile_photo","birthdate","gender","address",
        "education","skills","experience","projects","interests",
        "certifications","languages","contract_type","visa_status",
        "github_url","resume",
    )
    search_fields = ("user__username","user__email","github_url","visa_status","contract_type")
