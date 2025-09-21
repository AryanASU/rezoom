from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import home_view, debug_redirect_uri
urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("social_django.urls", namespace="social")),
    path("", include("accounts.urls")),
    path("jobs/", include("jobs.urls")),
    path("apps/", include("applications.urls")),
    path("interviews/", include("interviews.urls")),
    path("notifications/", include("notifications.urls")),   
    path("home/", home_view, name="home"),
    path("debug-redirect-uri/", debug_redirect_uri),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
