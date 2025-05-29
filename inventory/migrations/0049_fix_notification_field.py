from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0048_delete_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='employee_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='inventory.employee'),
        ),
    ] 