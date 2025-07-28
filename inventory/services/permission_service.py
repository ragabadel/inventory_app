from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from ..models import (
    PermissionGroup, UserAccessLog, OperationApproval,
    UserSession, ITAsset, Employee
)

class PermissionService:
    """Service class for handling permissions and access control"""

    @classmethod
    def initialize_permission_groups(cls):
        """Initialize default permission groups with proper inheritance"""
        with transaction.atomic():
            # Level 1: View Only
            view_only = PermissionGroup.objects.get_or_create(
                name='View Only',
                level=1,
                description='Can only view data, no modifications allowed'
            )[0]
            view_permissions = Permission.objects.filter(codename__startswith='view_')
            view_only.permissions.set(view_permissions)

            # Level 2: Basic Operations
            basic_ops = PermissionGroup.objects.get_or_create(
                name='Basic Operations',
                level=2,
                description='Can view and modify data, no deletions',
                parent=view_only
            )[0]
            basic_permissions = Permission.objects.filter(
                codename__in=['add_itasset', 'change_itasset', 'add_employee', 'change_employee']
            )
            basic_ops.permissions.set(basic_permissions)

            # Level 3: Full Access
            full_access = PermissionGroup.objects.get_or_create(
                name='Full Access',
                level=3,
                description='Full access except critical operations',
                parent=basic_ops
            )[0]
            excluded_permissions = Permission.objects.filter(
                codename__in=[
                    'delete_itasset', 'delete_employee', 'delete_department',
                    'delete_ownercompany', 'delete_outlet'
                ]
            )
            all_permissions = Permission.objects.exclude(id__in=excluded_permissions)
            full_access.permissions.set(all_permissions)

            # Level 4: Administrative
            admin_group = PermissionGroup.objects.get_or_create(
                name='Administrative',
                level=4,
                description='Complete administrative access',
                parent=full_access
            )[0]
            admin_group.permissions.set(Permission.objects.all())

    @classmethod
    def create_user_session(cls, user, request):
        """Create and validate user session"""
        session = UserSession.objects.create(
            user=user,
            session_key=request.session.session_key,
            ip_address=cls.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=timezone.now() + timezone.timedelta(
                seconds=settings.SESSION_COOKIE_AGE
            ),
            device_id=request.COOKIES.get('device_id', ''),
            location_data=cls.get_location_data(request)
        )
        return session

    @classmethod
    def log_user_action(cls, user, action, target_model, target_id=None, details=None, status='success', request=None):
        """Log user actions for audit trail"""
        UserAccessLog.objects.create(
            user=user,
            action=action,
            target_model=target_model,
            target_id=target_id,
            details=details or {},
            ip_address=cls.get_client_ip(request) if request else None,
            status=status,
            session_id=request.session.session_key if request else None
        )

    @classmethod
    def create_approval_request(cls, user, operation_type, target_model, target_ids, details=None, request=None):
        """Create an approval request for sensitive operations"""
        return OperationApproval.objects.create(
            requester=user,
            operation_type=operation_type,
            target_model=target_model,
            target_ids=target_ids,
            details=details or {},
            ip_address=cls.get_client_ip(request) if request else None
        )

    @classmethod
    def check_permission(cls, user, permission_codename, obj=None):
        """Check if user has permission, including object-level permissions"""
        if user.is_superuser:
            return True

        if obj is None:
            return user.has_perm(permission_codename)

        # Check object-level permissions
        content_type = ContentType.objects.get_for_model(obj)
        return user.has_perm(f"{content_type.app_label}.{permission_codename}", obj)

    @classmethod
    def get_client_ip(cls, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    @classmethod
    def get_location_data(cls, request):
        """Get location data from request"""
        return {
            'ip': cls.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referrer': request.META.get('HTTP_REFERER', ''),
            'timestamp': timezone.now().isoformat()
        }

    @classmethod
    def validate_session(cls, request):
        """Validate user session"""
        if not request.user.is_authenticated:
            return False

        try:
            session = UserSession.objects.get(
                user=request.user,
                session_key=request.session.session_key,
                is_active=True
            )
            return session.is_valid()
        except UserSession.DoesNotExist:
            return False

    @classmethod
    def requires_approval(cls, user, operation_type, target_model):
        """Check if operation requires approval"""
        if user.is_superuser:
            return False

        sensitive_operations = {
            'delete': True,
            'bulk_update': True,
            'sensitive_access': True,
            'export': True,
            'permission_change': True
        }

        return sensitive_operations.get(operation_type, False) 