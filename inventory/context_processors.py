from django.db.models import Q
from .models import Notification

def notification_count(request):
    """Context processor to add notification data to all templates."""
    context = {
        'unread_notifications_count': 0,
        'recent_notifications': [],
    }

    try:
        if request.user.is_authenticated:
            # Get unread notifications
            notifications = Notification.objects.select_related('category')

            # Check if user has an employee profile
            if hasattr(request.user, 'employee_profile') and request.user.employee_profile:
                notifications = notifications.filter(
                    Q(employee_profile=request.user.employee_profile) |
                    Q(employee_profile__isnull=True),
                    status='unread'
                )
            else:
                # If user doesn't have an employee profile, only show notifications without a specific employee
                notifications = notifications.filter(
                    employee_profile__isnull=True,
                    status='unread'
                )

            context['unread_notifications_count'] = notifications.count()
            context['recent_notifications'] = notifications.order_by('-created_at')[:5]
    except Exception:
        pass

    return context 