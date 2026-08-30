from .models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        return {
            'notifications': Notification.objects.filter(
                user=request.user
            ).order_by('-created_at')[:10],
            'unread_count': Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        }
    return {}
