from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import Group

class CustomPermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Custom permission mixin that handles permission checks and renders a custom 403 page"""
    
    permission_required = None  # Set this in the view
    
    def get_user_group_level(self):
        """Get the user's highest permission group level"""
        if self.request.user.is_superuser:
            return 4
            
        highest_level = 0
        for group in self.request.user.groups.all():
            group_config = settings.PERMISSION_GROUPS.get(group.name, {})
            level = group_config.get('level', 0)
            highest_level = max(highest_level, level)
        
        return highest_level

    def get_user_permissions(self):
        """Get the user's combined can/cannot permissions from all groups"""
        if self.request.user.is_superuser:
            return {'can': ['*'], 'cannot': []}
            
        can_permissions = set()
        cannot_permissions = set()
        
        for group in self.request.user.groups.all():
            group_config = settings.PERMISSION_GROUPS.get(group.name, {})
            can_permissions.update(group_config.get('can', []))
            cannot_permissions.update(group_config.get('cannot', []))
            
        return {
            'can': list(can_permissions),
            'cannot': list(cannot_permissions)
        }
    
    def check_permission(self, perm):
        """Check if user has permission and it's not in their cannot list"""
        permissions = self.get_user_permissions()
        
        # First check cannot list
        for cannot in permissions['cannot']:
            if cannot == '*' or cannot == perm or (cannot.endswith('_*') and perm.startswith(cannot[:-1])):
                return False
                
        # Then check can list
        for can in permissions['can']:
            if can == '*' or can == perm or (can.endswith('_*') and perm.startswith(can[:-1])):
                return True
                
        return False

    def test_func(self):
        # Check if user is superuser
        if self.request.user.is_superuser:
            return True
            
        # Check specific permissions
        if self.permission_required:
            if isinstance(self.permission_required, str):
                perms = (self.permission_required,)
            else:
                perms = self.permission_required
                
            # Check if user has all required permissions
            return all(self.check_permission(perm) for perm in perms)
            
        return False

    def handle_no_permission(self):
        group_info = []
        for group in self.request.user.groups.all():
            config = settings.PERMISSION_GROUPS.get(group.name, {})
            group_info.append({
                'name': group.name,
                'description': config.get('description', ''),
                'can': config.get('can', []),
                'cannot': config.get('cannot', [])
            })
            
        messages.error(self.request, _("You don't have permission to access this page."))
        return render(self.request, '403.html', {
            'groups': group_info,
            'required_permissions': self.permission_required
        }, status=403)

class ReadOnlyMixin(CustomPermissionMixin):
    """Mixin for views that should be read-only for regular users"""
    
    def test_func(self):
        # Allow view access but restrict modifications
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return super().test_func()

class NoDeleteMixin(CustomPermissionMixin):
    """Mixin that prevents deletion for non-admin users"""
    
    def test_func(self):
        if self.request.method == 'DELETE' or self.request.POST.get('action') == 'delete':
            # Check if operation requires approval
            operation = f'delete_{self.model._meta.model_name}'
            if operation in settings.OPERATIONS_REQUIRING_APPROVAL:
                messages.warning(self.request, _('This operation requires approval from an administrator.'))
                return False
                
            # Check if operation is critical
            if operation in settings.CRITICAL_OPERATIONS:
                return self.request.user.is_superuser
                
            # Check regular permissions
            return self.check_permission(operation)
        return True 