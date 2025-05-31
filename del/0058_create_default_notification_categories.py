from django.db import migrations

def create_notification_categories(apps, schema_editor):
    NotificationCategory = apps.get_model('inventory', 'NotificationCategory')
    
    categories = [
        {
            'name': 'Device Assignment',
            'icon': 'fa-laptop',
            'color': 'primary',
            'description': 'Notifications about device assignments and returns'
        },
        {
            'name': 'Maintenance',
            'icon': 'fa-tools',
            'color': 'warning',
            'description': 'Notifications about device maintenance and repairs'
        },
        {
            'name': 'System',
            'icon': 'fa-cog',
            'color': 'secondary',
            'description': 'System notifications and updates'
        },
        {
            'name': 'Warranty',
            'icon': 'fa-shield-alt',
            'color': 'warning',
            'description': 'Notifications about warranty status and expiration'
        },
        {
            'name': 'Device Modification',
            'icon': 'fa-edit',
            'color': 'info',
            'description': 'Notifications about device modifications and updates'
        }
    ]
    
    # Clear existing categories first to avoid duplicates
    NotificationCategory.objects.all().delete()
    
    # Create new categories
    for category_data in categories:
        NotificationCategory.objects.create(**category_data)

def reverse_func(apps, schema_editor):
    NotificationCategory = apps.get_model('inventory', 'NotificationCategory')
    NotificationCategory.objects.filter(name__in=[
        'Device Assignment',
        'Maintenance',
        'System',
        'Warranty',
        'Device Modification'
    ]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0057_merge_all_migrations'),
    ]

    operations = [
        migrations.RunPython(create_notification_categories, reverse_func),
    ] 