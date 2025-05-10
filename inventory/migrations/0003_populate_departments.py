from django.db import migrations

def populate_departments(apps, schema_editor):
    Department = apps.get_model('inventory', 'Department')
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
        Department.objects.get_or_create(
            name=code,
            defaults={'description': f'Department of {name}'}
        )

def reverse_populate_departments(apps, schema_editor):
    Department = apps.get_model('inventory', 'Department')
    Department.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0002_department_alter_itasset_options_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_departments, reverse_populate_departments),
    ] 