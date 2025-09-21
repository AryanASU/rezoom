def unread_notifications(request):
    if not request.user.is_authenticated:
        return {"unread_count": 0, "recent_notifications": []}
    qs = request.user.notifications.filter(is_read=False)[:10]
    return {
        "unread_count": qs.count(),
        "recent_notifications": qs,
    }
