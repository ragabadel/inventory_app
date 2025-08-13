from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone

from .services.permission_service import PermissionService


@receiver(user_logged_in)
def create_user_session_on_login(sender, user, request, **kwargs):
    try:
        PermissionService.create_user_session(user, request)
    except Exception:
        pass


@receiver(user_logged_out)
def deactivate_user_session_on_logout(sender, user, request, **kwargs):
    try:
        from .models import UserSession
        if not user or not request:
            return
        UserSession.objects.filter(
            user=user,
            session_key=getattr(request.session, 'session_key', None),
            is_active=True,
        ).update(is_active=False, last_activity=timezone.now())
    except Exception:
        pass


