from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from inventory.models import Employee, Department, Position, OwnerCompany

class Command(BaseCommand):
    help = 'Creates system users with their respective groups and permissions'

    def handle(self, *args, **kwargs):
        # Create groups if they don't exist
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        it_support_group, _ = Group.objects.get_or_create(name='IT Support')
        technician_group, _ = Group.objects.get_or_create(name='Technician')

        # Get all model content types for permissions
        content_types = ContentType.objects.all()
        
        # Assign permissions to groups
        # Admin gets all permissions
        admin_permissions = Permission.objects.all()
        admin_group.permissions.set(admin_permissions)

        # IT Support permissions
        it_support_permissions = Permission.objects.filter(
            content_type__model__in=[
                'itasset', 'employee', 'department', 'position',
                'owncompany', 'assettype', 'assethistory', 'notification'
            ]
        )
        it_support_group.permissions.set(it_support_permissions)

        # Technician permissions (limited to maintenance and basic viewing)
        technician_permissions = Permission.objects.filter(
            content_type__model__in=['itasset', 'assethistory'],
            codename__in=['view_itasset', 'change_itasset', 'view_assethistory', 'add_assethistory']
        )
        technician_group.permissions.set(technician_permissions)

        # Create or update system users
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'Admin@123',
                'first_name': 'System',
                'last_name': 'Administrator',
                'groups': [admin_group],
                'employee_id': 'ADM001',
                'position': 'System Administrator',
                'department': 'it'
            },
            {
                'username': 'it_support',
                'email': 'it.support@example.com',
                'password': 'IT@123',
                'first_name': 'IT',
                'last_name': 'Support',
                'groups': [it_support_group],
                'employee_id': 'ITS001',
                'position': 'IT Support Specialist',
                'department': 'it'
            },
            {
                'username': 'technician',
                'email': 'technician@example.com',
                'password': 'Tech@123',
                'first_name': 'System',
                'last_name': 'Technician',
                'groups': [technician_group],
                'employee_id': 'TEC001',
                'position': 'IT Technician',
                'department': 'it'
            }
        ]

        # Create default company if it doesn't exist
        company, _ = OwnerCompany.objects.get_or_create(
            code='CTP',
            name='CTP'
        )

        for user_data in users_data:
            # Create or update user
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': True,
                    'is_active': True
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created user "{user.username}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'User "{user.username}" already exists')
                )

            # Set user groups
            user.groups.set(user_data['groups'])

            # Create or update employee profile
            department = Department.objects.get(name=user_data['department'])
            position, _ = Position.objects.get_or_create(
                name=user_data['position'],
                department=department
            )

            employee, created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': user_data['employee_id'],
                    'national_id': f'0000000000000{user_data["employee_id"][-3:]}',
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email'],
                    'department': department,
                    'position': position,
                    'company': company,
                    'hire_date': '2024-01-01'
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created employee profile for "{user.username}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Employee profile for "{user.username}" already exists')
                )

        self.stdout.write(self.style.SUCCESS('Successfully set up system users')) 