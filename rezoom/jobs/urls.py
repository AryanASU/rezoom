from django.urls import path
from .views import job_create, job_detail, employees_json, job_browse, job_public_detail

urlpatterns = [
    path("", job_browse, name="job_browse"),                     # /jobs/
    path("new/", job_create, name="job_create"),                 # HR
    path("<int:pk>/", job_detail, name="job_detail"),            # HR private detail
    path("view/<int:pk>/", job_public_detail, name="job_public_detail"),  # user-facing detail
    path("employees-json/<int:company_id>/", employees_json, name="employees_json"),
]
