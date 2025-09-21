from django.urls import path
from .views import availability_list, availability_add, availability_delete, schedule_invite, pending_confirms, confirm_interview

urlpatterns = [
    path("availability/", availability_list, name="availability_list"),
    path("availability/add/", availability_add, name="availability_add"),
    path("availability/delete/<int:slot_id>/", availability_delete, name="availability_delete"),

    path("schedule/<int:app_id>/", schedule_invite, name="schedule_invite"),
    path("pending/", pending_confirms, name="pending_confirms"),
    path("confirm/<int:interview_id>/", confirm_interview, name="confirm_interview"),
]
