from django.contrib import admin
from .models import Company, Employee

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "created_by", "created_at")
    search_fields = ("name", "domain")
    fields = ("name","domain","address","logo","created_by")  # show logo uploader

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "job_role", "years_exp", "is_active")
    list_filter = ("company", "is_active")
    search_fields = ("user__username", "user__email", "job_role")
    fields = ("user","company","job_role","years_exp","is_active","photo")  # show photo uploader

from .models import Company, Employee, OfficeLocation

@admin.register(OfficeLocation)
class OfficeLocationAdmin(admin.ModelAdmin):
    list_display = ("company","label","room")
    list_filter = ("company",)
    search_fields = ("label","room","address")
