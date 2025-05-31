from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0040_fix_notification_employee'),
        ('inventory', '0041_update_employee_position_field'),
        ('inventory', '0042_devicehistory_alter_employee_options'),
        ('inventory', '0042_fix_postgres_position_column'),
        ('inventory', '0043_fix_position_reference'),
        ('inventory', '0043_merge_20250525_1418'),
        ('inventory', '0044_merge_20250525_1420'),
        ('inventory', '0045_merge_20250525_1435'),
    ]

    operations = [
    ] 