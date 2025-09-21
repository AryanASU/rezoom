from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import ProfileForm
from django.contrib import messages
from jobs.models import JobAssignee
from django.shortcuts import render, redirect
from django.urls import reverse, NoReverseMatch
from django.http import HttpResponseRedirect, HttpResponse

def login_view(request):
    if request.user.is_authenticated:
        return redirect("portal")

    # Build Google begin URL safely
    try:
        google_begin = reverse("social:begin", args=["google-oauth2"])
    except NoReverseMatch:
        # Fallback to default social_django path if not namespaced yet
        google_begin = "/auth/login/google-oauth2/"
    try:
        nxt = reverse("portal")
    except NoReverseMatch:
        nxt = "/portal/"
    oauth_url = f"{google_begin}?next={nxt}"

    msg = request.GET.get("message") or request.GET.get("error") or ""
    return render(request, "accounts/login.html", {"oauth_url": oauth_url, "auth_error": msg})

def debug_redirect_uri(request):
    # This is the redirect URI social-auth will call back to.
    uri = request.build_absolute_uri(reverse("social:complete", args=["google-oauth2"]))
    return HttpResponse(uri, content_type="text/plain")

def logout_view(request):
    logout(request)
    return redirect("login")
def go_google_view(request):
    """
    Pure server-side redirect to Google login. If this works,
    your social_django routing & keys are fine.
    """
    try:
        begin = reverse("social:begin", args=["google-oauth2"])
    except NoReverseMatch:
        begin = "/auth/login/google-oauth2/"
    return HttpResponseRedirect(begin + "?next=/portal/")
def home_view(request):
    """
    Public landing page. Builds a Google OAuth URL for CTA.
    Never redirects away; visible even when logged out.
    """
    # Build Google begin URL safely (with fallbacks so href is NEVER empty)
    try:
        google_begin = reverse("social:begin", args=["google-oauth2"])
    except NoReverseMatch:
        google_begin = "/auth/login/google-oauth2/"  # default from social_django

    try:
        nxt = reverse("portal")
    except NoReverseMatch:
        nxt = "/portal/"

    oauth_url = f"{google_begin}?next={nxt}"
    return render(request, "home.html", {"oauth_url": oauth_url})

@login_required
def role_router(request):
    # Company logic later can refine this; for now use User.role
    r = request.user.role
    if r == "HR":   return redirect("hr_dashboard")
    if r == "EMP":  return redirect("emp_dashboard")
    return redirect("user_dashboard")  # default USER

@login_required
def user_dashboard(request):
    apps = (
        request.user.applications
        .select_related("job", "job__company")
        .order_by("-created_at")
    )
    return render(request, "accounts/user_dashboard.html", {"apps": apps})
@login_required
def hr_dashboard(request):
    return render(request, "accounts/hr_dashboard.html")

@login_required
def emp_dashboard(request):
    return render(request, "accounts/emp_dashboard.html")

def login_view(request):
    return render(request, "accounts/login.html")

from django.shortcuts import render, redirect
# ...

def home(request):
    # if already signed in, go to role router; else show login
    if request.user.is_authenticated:
        return redirect("portal")
    return redirect("login")

@login_required
def profile_edit(request):
    prof = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=prof, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile saved.")
            return redirect("user_dashboard")
    else:
        form = ProfileForm(instance=prof, user=request.user)
    return render(request, "accounts/profile_edit.html", {"form": form})

@login_required
def emp_dashboard(request):
    invites = JobAssignee.objects.select_related("job__company","employee").filter(
        employee__user=request.user
    ).order_by("-id")
    return render(request, "accounts/emp_dashboard.html", {"invites": invites})

