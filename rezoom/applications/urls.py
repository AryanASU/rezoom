from django.urls import path
from .views import apply_to_job, employee_queue, queue_decide, build_queue

urlpatterns = [
    path("apply/<int:job_id>/", apply_to_job, name="apply_job"),
    path("queue/", employee_queue, name="employee_queue"),
    path("queue/build/", build_queue, name="build_queue"),
    path("queue/decide/<int:aa_id>/", queue_decide, name="queue_decide"),
]
