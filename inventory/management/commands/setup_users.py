from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from inventory.models import Employee, Department, Position, OwnerCompany
from django.db.models import Q
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates enterprise-grade system users with role-based access control (RBAC)'

    def handle(self, *args, **kwargs):
        # Create enterprise role groups with hierarchical structure
        roles = {
            'system_administrator': {
                'name': 'System Administrator',
                'description': 'Complete system control with full administrative privileges',
                'level': 1  # Top level access
            },
            'system_admin': {
                'name': 'System Admin',
                'description': 'System administration with restricted sensitive operations',
                'level': 2  # Second level access
            },
            'help_desk': {
                'name': 'Help Desk',
                'description': 'Front-line IT support and user assistance',
                'level': 3  # Third level access
            }
        }

        # Create groups with metadata
        created_groups = {}
        for role_key, role_data in roles.items():
            group, _ = Group.objects.get_or_create(name=role_data['name'])
            created_groups[role_key] = group
            self.stdout.write(
                self.style.SUCCESS(f'Role configured: {role_data["name"]} (Level {role_data["level"]})')
            )

        # Enhanced permission assignments
        # System Administrator - Full system access
        system_administrator_permissions = Permission.objects.all()
        created_groups['system_administrator'].permissions.set(system_administrator_permissions)

        # System Admin - Comprehensive management permissions
        system_admin_permissions = Permission.objects.filter(
            Q(content_type__model__in=[
                'itasset', 'employee', 'department', 'position',
                'owncompany', 'assettype', 'assethistory', 'notification'
            ]) &
            (Q(codename__startswith='view_') | 
             Q(codename__startswith='change_') |
             Q(codename__startswith='add_'))
        ).exclude(
            # Exclude sensitive operations
            Q(codename__startswith='delete_') |
            Q(content_type__model__in=['user', 'group'])
        )
        created_groups['system_admin'].permissions.set(system_admin_permissions)

        # Help Desk - User support focused permissions
        help_desk_permissions = Permission.objects.filter(
            Q(content_type__model__in=['itasset', 'employee'], codename__startswith='view_') |
            Q(content_type__model='assethistory', codename__in=[
                'view_assethistory',
                'add_assethistory',
                'change_assethistory'
            ]) |
            Q(content_type__model='notification', codename__in=[
                'view_notification',
                'add_notification'
            ])
        )
        created_groups['help_desk'].permissions.set(help_desk_permissions)

        # Enterprise user profiles
        enterprise_users = [
            {
                'username': 'sysadmin',
                'email': 'sysadmin@company.com',
                'password': 'SysAdmin@2024!',
                'first_name': 'System',
                'last_name': 'Administrator',
                'groups': [created_groups['system_administrator']],
                'employee_id': 'SA1001',
                'position': 'Enterprise System Administrator',
                'department': 'it',
                'phone': '+1234567890',
                'office_location': 'HQ-IT-01',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'username': 'sysops',
                'email': 'sysops@company.com',
                'password': 'SysOps@2024!',
                'first_name': 'System',
                'last_name': 'Operations',
                'groups': [created_groups['system_admin']],
                'employee_id': 'SO1001',
                'position': 'System Operations Manager',
                'department': 'it',
                'phone': '+1234567891',
                'office_location': 'HQ-IT-02',
                'is_staff': True,
                'is_superuser': False
            },
            {
                'username': 'helpdesk',
                'email': 'helpdesk@company.com',
                'password': 'HelpDesk@2024!',
                'first_name': 'IT',
                'last_name': 'Support',
                'groups': [created_groups['help_desk']],
                'employee_id': 'HD1001',
                'position': 'IT Support Specialist',
                'department': 'it',
                'phone': '+1234567892',
                'office_location': 'HQ-IT-03',
                'is_staff': True,
                'is_superuser': False
            }
        ]

        # Create default company with proper corporate structure
        company, _ = OwnerCompany.objects.get_or_create(
            code='CORP',
            name='Corporate Headquarters'
        )

        # Create or update enterprise users
        for user_data in enterprise_users:
            # Create or update user with enhanced security
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': user_data['is_staff'],
                    'is_superuser': user_data.get('is_superuser', False),
                    'is_active': True
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Enterprise user created: {user.username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Enterprise user exists: {user.username}')
                )

            # Set user groups
            user.groups.set(user_data['groups'])

            # Create or update department
            department = Department.objects.get(name=user_data['department'])
            
            # Create or update position with enhanced details
            position, _ = Position.objects.get_or_create(
                name=user_data['position'],
                department=department,
                defaults={
                    'description': f'Enterprise role for {user_data["position"]}'
                }
            )

            # Create or update employee profile with enhanced corporate details
            employee, created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': user_data['employee_id'],
                    'national_id': f'{user_data["employee_id"]}ENT',
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email'],
                    'phone_number': user_data['phone'],
                    'department': department,
                    'position': position,
                    'company': company,
                    'hire_date': timezone.now().date(),
                    'is_active': True
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Enterprise profile created: {user.get_full_name()} ({position.name})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Enterprise profile exists: {user.get_full_name()} ({position.name})')
                )

        self.stdout.write(
            self.style.SUCCESS('Enterprise user setup completed successfully')
        ) 