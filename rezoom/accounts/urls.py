from django.urls import path
from .views import login_view, logout_view, role_router, user_dashboard, hr_dashboard, emp_dashboard, profile_edit

urlpatterns = [
    path("",                 login_view,    name="home"),  # or your home handler
    path("login/",           login_view,    name="login"),
    path("logout/",          logout_view,   name="logout"),
    path("portal/",          role_router,   name="portal"),
    path("u/",               user_dashboard, name="user_dashboard"),
    path("u/profile/",       profile_edit,   name="profile_edit"),   # ← new
    path("hr/",              hr_dashboard,   name="hr_dashboard"),
    path("emp/",             emp_dashboard,  name="emp_dashboard"),
]
