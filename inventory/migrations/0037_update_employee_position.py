from django.db import migrations, models
import django.db.models.deletion

def create_positions_from_employees(apps, schema_editor):
    """Create Position objects from existing employee position data"""
    Employee = apps.get_model('inventory', 'Employee')
    Position = apps.get_model('inventory', 'Position')
    Department = apps.get_model('inventory', 'Department')
    
    # Get all unique position-department combinations
    positions = set()
    for emp in Employee.objects.all():
        if emp.position_data and emp.department:
            positions.add((emp.position_data, emp.department))
    
    # Create Position objects
    position_map = {}
    for pos_name, dept in positions:
        position, _ = Position.objects.get_or_create(
            name=pos_name,
            department=dept
        )
        position_map[(pos_name, dept.id)] = position

def link_employees_to_positions(apps, schema_editor):
    """Link employees to their corresponding Position objects"""
    Employee = apps.get_model('inventory', 'Employee')
    Position = apps.get_model('inventory', 'Position')
    
    for emp in Employee.objects.all():
        if emp.position_data and emp.department:
            try:
                position = Position.objects.get(
                    name=emp.position_data,
                    department=emp.department
                )
                # Update the position directly
                Employee.objects.filter(id=emp.id).update(position=position)
            except Position.DoesNotExist:
                # If position doesn't exist, create it
                position = Position.objects.create(
                    name=emp.position_data,
                    department=emp.department
                )
                # Update the position directly
                Employee.objects.filter(id=emp.id).update(position=position)

def reverse_position_migration(apps, schema_editor):
    """Reverse the position migration"""
    Employee = apps.get_model('inventory', 'Employee')
    Position = apps.get_model('inventory', 'Position')
    for emp in Employee.objects.all():
        if emp.position:
            Employee.objects.filter(id=emp.id).update(position_data=emp.position.name)

class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0030_auto_20250521_2044'),
    ]

    operations = [
        # Add temporary field to store position data
        migrations.AddField(
            model_name='employee',
            name='position_data',
            field=models.CharField(max_length=100, null=True),
        ),
        
        # Store current position data
        migrations.RunPython(
            lambda apps, schema_editor: None,  # No-op forward function
            lambda apps, schema_editor: None,  # No-op reverse function
        ),
        
        # Create positions and link employees
        migrations.RunPython(
            create_positions_from_employees,
            reverse_position_migration
        ),
        
        # Remove the temporary position_data field
        migrations.RemoveField(
            model_name='employee',
            name='position_data',
        ),
    ] 