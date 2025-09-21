from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Notification

@login_required
def list_notifications(request):
    items = request.user.notifications.all()[:200]
    return render(request, "notifications/list.html", {"items": items})

@login_required
def mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save(update_fields=["is_read"])
    if n.url:
        return redirect(n.url)
    messages.info(request, "Notification marked as read.")
    return redirect("notifications_list")

@login_required
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect("notifications_list")
