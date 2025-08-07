from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from inventory.models import (
    PermissionGroup, ITAsset, Employee, Department,
    OwnerCompany, Outlet
)

class Command(BaseCommand):
    help = 'Initialize permission groups and assign permissions'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Create permission groups
                self.stdout.write('Creating permission groups...')
                
                # Level 1: View Only
                view_only = PermissionGroup.objects.get_or_create(
                    name='View Only',
                    level=1,
                    description='Can only view data, no modifications allowed'
                )[0]
                
                # Get all view permissions
                view_permissions = Permission.objects.filter(codename__startswith='view_')
                view_only.permissions.set(view_permissions)
                self.stdout.write(f'Added {view_permissions.count()} view permissions to View Only group')

                # Level 2: Basic Operations
                basic_ops = PermissionGroup.objects.get_or_create(
                    name='Basic Operations',
                    level=2,
                    description='Can view and modify data, no deletions',
                    parent=view_only
                )[0]
                
                # Get basic operation permissions
                basic_permissions = Permission.objects.filter(
                    codename__in=[
                        'add_itasset', 'change_itasset',
                        'add_employee', 'change_employee',
                        'add_department', 'change_department'
                    ]
                )
                basic_ops.permissions.set(basic_permissions)
                self.stdout.write(f'Added {basic_permissions.count()} permissions to Basic Operations group')

                # Level 3: Full Access
                full_access = PermissionGroup.objects.get_or_create(
                    name='Full Access',
                    level=3,
                    description='Full access except critical operations',
                    parent=basic_ops
                )[0]
                
                # Exclude critical permissions
                excluded_permissions = Permission.objects.filter(
                    codename__in=[
                        'delete_itasset', 'delete_employee',
                        'delete_department', 'delete_ownercompany',
                        'delete_outlet'
                    ]
                )
                all_permissions = Permission.objects.exclude(id__in=excluded_permissions)
                full_access.permissions.set(all_permissions)
                self.stdout.write(f'Added {all_permissions.count()} permissions to Full Access group')

                # Level 4: Administrative
                admin_group = PermissionGroup.objects.get_or_create(
                    name='Administrative',
                    level=4,
                    description='Complete administrative access',
                    parent=full_access
                )[0]
                admin_group.permissions.set(Permission.objects.all())
                self.stdout.write(f'Added {Permission.objects.count()} permissions to Administrative group')

                # Create corresponding Django groups
                django_groups = {
                    'View Only': view_only,
                    'Basic Operations': basic_ops,
                    'Full Access': full_access,
                    'Administrative': admin_group
                }

                for name, perm_group in django_groups.items():
                    group = Group.objects.get_or_create(name=name)[0]
                    group.permissions.set(perm_group.permissions.all())
                    self.stdout.write(f'Created/Updated Django group: {name}')

                self.stdout.write(self.style.SUCCESS('Successfully initialized permission groups'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error initializing permissions: {str(e)}'))
            raise 