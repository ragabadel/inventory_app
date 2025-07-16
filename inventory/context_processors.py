from django.db.models import Q
from .models import Notification
from django.contrib.auth.models import User

def notification_context(request):
    """Context processor for notifications"""
    if request.user.is_authenticated:
        # Build the filter based on user's employee profile
        if hasattr(request.user, 'employee_profile') and request.user.employee_profile:
            notification_filter = Q(
                Q(employee_profile=request.user.employee_profile) |
                Q(employee_profile__isnull=True)
            )
        else:
            notification_filter = Q(employee_profile__isnull=True)
        
        # Get unread notifications count
        unread_count = Notification.objects.filter(
            notification_filter,
            status='unread'
        ).count()
        
        # Get recent notifications for dropdown
        notifications = Notification.objects.filter(
            notification_filter
        ).exclude(
            status='archived'
        ).select_related(
            'category'
        ).order_by(
            '-status',  # This will put unread first since 'unread' > 'read'
            '-created_at'
        )[:10]
        
        return {
            'notifications': notifications,
            'unread_notifications_count': unread_count
        }
    return {
        'notifications': [],
        'unread_notifications_count': 0
    } 

def superuser_check(request):
    """Check if any superuser exists in the system."""
    return {
        'has_superuser': User.objects.filter(is_superuser=True).exists()
    } 