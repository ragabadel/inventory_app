from django.core.management.base import BaseCommand
from inventory.models import Department, Employee
from datetime import date

class Command(BaseCommand):
    help = 'Creates test departments and a test employee'

    def handle(self, *args, **kwargs):
        # Create departments
        departments = [
            ('warehouse', 'Warehouse'),
            ('hr', 'HR'),
            ('procurement', 'Procurement'),
            ('quality', 'Quality'),
            ('finance', 'Finance'),
            ('production', 'Production'),
            ('maintenance', 'Maintenance'),
            ('osh', 'Occupational Safety and Health'),
            ('it', 'IT'),
        ]

        for code, name in departments:
            dept, created = Department.objects.get_or_create(
                name=code,
                defaults={'description': f'Department of {name}'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created department: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Department already exists: {name}'))

        # Create test employee
        try:
            # First, delete any existing test employee
            Employee.objects.filter(employee_id='EMP001').delete()
            
            employee = Employee.objects.create(
                employee_id='EMP001',
                first_name='John',
                last_name='Doe',
                email='john.doe.test@example.com',  # Changed email to avoid conflict
                phone_number='1234567890',
                department=Department.objects.get(name='it'),
                position='Software Developer',
                hire_date=date.today(),
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created test employee: {employee}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating employee: {str(e)}')) 