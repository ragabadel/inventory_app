from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0056_handle_company_model'),
        ('inventory', '0056_merge_20250531_2100'),
        ('inventory', '0055_fix_notification_schema'),
        ('inventory', '0054_create_notification_categories'),
        ('inventory', '0052_add_default_notification_categories'),
        ('inventory', '0053_remove_notification_is_email_sent_and_more'),
        ('inventory', '0051_rename_inventory_n_employe_a440fc_idx_inventory_n_employe_37314b_idx'),
        ('inventory', '0050_notification_system'),
        ('inventory', '0049_fix_notification_field'),
        ('inventory', '0048_delete_company'),
    ]

    operations = [
    ] 