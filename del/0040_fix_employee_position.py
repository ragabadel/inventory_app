from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0039_notification'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='position',
            new_name='position_id',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='position_id',
            new_name='position',
        ),
    ] 