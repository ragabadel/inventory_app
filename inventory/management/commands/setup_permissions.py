from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.apps import apps

class Command(BaseCommand):
    help = 'Set up initial permission groups and assign permissions'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up permission groups...')

        # Create default groups
        for group_name, config in settings.PERMISSION_GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f'Created group: {group_name}')
            else:
                self.stdout.write(f'Updated group: {group_name}')

            # Get all models from the app
            app_models = apps.get_app_config('inventory').get_models()
            
            # Collect permissions for this group
            permissions = set()
            
            # Process 'can' permissions
            for model in app_models:
                content_type = ContentType.objects.get_for_model(model)
                model_name = model._meta.model_name
                
                for perm_pattern in config.get('can', []):
                    if perm_pattern == '*':
                        # Add all permissions for this model
                        perms = Permission.objects.filter(content_type=content_type)
                        permissions.update(perms)
                    else:
                        # Add specific permission type (e.g., 'view_*')
                        if perm_pattern.endswith('_*'):
                            perm_type = perm_pattern.split('_')[0]
                            perms = Permission.objects.filter(
                                content_type=content_type,
                                codename__startswith=f"{perm_type}_"
                            )
                            permissions.update(perms)
                        else:
                            # Exact permission match
                            try:
                                perm = Permission.objects.get(
                                    content_type=content_type,
                                    codename=perm_pattern
                                )
                                permissions.add(perm)
                            except Permission.DoesNotExist:
                                self.stdout.write(f'Permission not found: {perm_pattern}')
            
            # Remove 'cannot' permissions
            for model in app_models:
                content_type = ContentType.objects.get_for_model(model)
                model_name = model._meta.model_name
                
                for perm_pattern in config.get('cannot', []):
                    if perm_pattern == '*':
                        # Remove all permissions for this model
                        perms = Permission.objects.filter(content_type=content_type)
                        permissions.difference_update(perms)
                    else:
                        # Remove specific permission type
                        if perm_pattern.endswith('_*'):
                            perm_type = perm_pattern.split('_')[0]
                            perms = Permission.objects.filter(
                                content_type=content_type,
                                codename__startswith=f"{perm_type}_"
                            )
                            permissions.difference_update(perms)
                        else:
                            # Exact permission match
                            try:
                                perm = Permission.objects.get(
                                    content_type=content_type,
                                    codename=perm_pattern
                                )
                                permissions.discard(perm)
                            except Permission.DoesNotExist:
                                self.stdout.write(f'Permission not found: {perm_pattern}')

            # Set permissions for the group
            group.permissions.set(permissions)
            self.stdout.write(f'Added {len(permissions)} permissions to {group_name}')

        self.stdout.write(self.style.SUCCESS('Successfully set up permission groups')) 