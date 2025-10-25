from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import resolve, reverse
from django.utils import timezone
from .services.permission_service import PermissionService
from django.http import HttpResponseForbidden
import json

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define exempt paths that don't require authentication checks
        exempt_prefixes = [
            'static/',
            'media/',
            'i18n/',
            'accounts/login/',
            'accounts/logout/',
            'accounts/register/',
        ]

        # Check if the current path is exempt
        current_path = request.path.lstrip('/')
        language_prefix = current_path.split('/')[0] if current_path else ''
        path_without_lang = '/'.join(current_path.split('/')[1:])

        # Skip middleware for exempt paths and non-authenticated users
        if path_without_lang == '' or any(path_without_lang.startswith(prefix) for prefix in exempt_prefixes):
            return self.get_response(request)

        # If user is not authenticated, redirect to login
        if not request.user.is_authenticated:
            login_url = f'/{language_prefix}/accounts/login/'
            # Avoid redirect loop: if we're already on login, let it proceed
            if path_without_lang.startswith('accounts/login'):
                return self.get_response(request)
            return redirect(f'{login_url}?next={request.path}')

        # Validate session for authenticated users
        if not PermissionService.validate_session(request):
            messages.error(request, _('Your session has expired. Please log in again.'))
            return redirect(f'/{language_prefix}/accounts/login/')

        # Get current view
        try:
            current_url = resolve(request.path_info)
            view_name = current_url.url_name

            # Check if operation requires approval
            if request.method in ['POST', 'PUT', 'DELETE']:
                operation_type = self._get_operation_type(request)
                if operation_type and PermissionService.requires_approval(request.user, operation_type, current_url.app_name):
                    return self._handle_approval_required(request, operation_type)

            # Log the access
            PermissionService.log_user_action(
                user=request.user,
                action=f"{request.method}_{view_name}",
                target_model=current_url.app_name,
                request=request
            )

        except Exception as e:
            # Log the error but don't block the request
            print(f"Error in SecurityMiddleware: {str(e)}")

        response = self.get_response(request)

        # Update session activity
        if hasattr(request, 'user_session'):
            request.user_session.last_activity = timezone.now()
            request.user_session.save()

        return response

    def _get_operation_type(self, request):
        """Determine the type of operation being performed"""
        if request.method == 'DELETE':
            return 'delete'
        if request.method == 'POST':
            if 'bulk' in request.POST:
                return 'bulk_update'
            if 'export' in request.POST:
                return 'export'
            if 'permission' in request.POST:
                return 'permission_change'
        return None

    def _handle_approval_required(self, request, operation_type):
        """Handle operations that require approval"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponseForbidden(
                _('This operation requires approval. Please submit an approval request.')
            )

        messages.warning(
            request,
            _('This operation requires approval. An approval request has been created.')
        )

        PermissionService.create_approval_request(
            user=request.user,
            operation_type=operation_type,
            target_model=resolve(request.path_info).app_name,
            target_ids=self._get_target_ids(request),
            request=request
        )

        return redirect(request.path)

    def _get_target_ids(self, request):
        """Extract target IDs from request"""
        if request.method == 'POST':
            return request.POST.getlist('ids[]') or [request.POST.get('id')]
        return []

class DataMaskingMiddleware:
    """Middleware for masking sensitive data"""
    SENSITIVE_FIELDS = {
        'national_id': lambda x: f"{'*' * (len(x)-4)}{x[-4:]}",
        'phone_number': lambda x: f"{'*' * (len(x)-4)}{x[-4:]}",
        'email': lambda x: f"{x[0]}{'*' * (len(x.split('@')[0])-2)}{x[0]}@{x.split('@')[1]}",
        'mac_address_wifi': lambda x: f"{'*' * 8}{x[-4:]}",
        'mac_address_ethernet': lambda x: f"{'*' * 8}{x[-4:]}",
        'ip_address': lambda x: f"{'*' * (len(x.split('.')[0]))}.{'.'.join(x.split('.')[1:])}"
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only process JSON responses
        if not hasattr(response, 'content_type') or 'application/json' not in response.content_type:
            return response

        # Check if user has permission to view sensitive data
        if request.user.has_perm('inventory.view_sensitive_data'):
            return response

        # Mask sensitive data in response
        try:
            data = response.json()
            masked_data = self._mask_sensitive_data(data)
            response.content = json.dumps(masked_data)
        except (ValueError, AttributeError):
            pass

        return response

    def _mask_sensitive_data(self, data):
        """Recursively mask sensitive data in response"""
        if isinstance(data, dict):
            return {
                key: (
                    self.SENSITIVE_FIELDS[key](value)
                    if key in self.SENSITIVE_FIELDS and value
                    else self._mask_sensitive_data(value)
                )
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        return data 