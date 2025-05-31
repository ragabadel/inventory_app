from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0039_notification'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='employee',
            new_name='employee_profile',
        ),
    ] 