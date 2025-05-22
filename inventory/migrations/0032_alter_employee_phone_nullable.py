from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0031_notification_workflowrequest_delete_company_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='phone_number',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ] 