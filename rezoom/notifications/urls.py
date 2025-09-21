# notifications/urls.py
from django.urls import path
from .views import list_notifications, mark_read, mark_all_read

urlpatterns = [
    path("", list_notifications, name="notifications_list"),
    path("read/<int:pk>/", mark_read, name="notifications_read"),
    path("read-all/", mark_all_read, name="notifications_read_all"),
]
