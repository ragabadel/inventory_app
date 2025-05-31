from django.db import migrations

def create_notification_categories(apps, schema_editor):
    NotificationCategory = apps.get_model('inventory', 'NotificationCategory')
    
    categories = [
        {
            'name': 'System',
            'icon': 'fas fa-cog',
            'color': '#6c757d',  # Gray
            'description': 'System notifications and updates'
        },
        {
            'name': 'Device Assignment',
            'icon': 'fas fa-laptop',
            'color': '#28a745',  # Green
            'description': 'Device assignment and return notifications'
        },
        {
            'name': 'Warranty',
            'icon': 'fas fa-shield-alt',
            'color': '#ffc107',  # Yellow
            'description': 'Warranty expiration notifications'
        },
        {
            'name': 'Maintenance',
            'icon': 'fas fa-tools',
            'color': '#dc3545',  # Red
            'description': 'Device maintenance notifications'
        }
    ]
    
    for category_data in categories:
        NotificationCategory.objects.get_or_create(
            name=category_data['name'],
            defaults=category_data
        )

def reverse_notification_categories(apps, schema_editor):
    NotificationCategory = apps.get_model('inventory', 'NotificationCategory')
    NotificationCategory.objects.filter(
        name__in=['System', 'Device Assignment', 'Warranty', 'Maintenance']
    ).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0053_remove_notification_is_email_sent_and_more'),
    ]

    operations = [
        migrations.RunPython(
            create_notification_categories,
            reverse_notification_categories
        ),
    ] 