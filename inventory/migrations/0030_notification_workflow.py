from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('inventory', '0028_alter_employee_employee_id_assethistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('warranty_expiry', 'Warranty Expiry'), ('serial_expiry', 'Serial Expiry'), ('new_device_request', 'New Device Request'), ('maintenance_request', 'Maintenance Request'), ('damaged_device', 'Damaged Device'), ('lost_device', 'Lost Device')], max_length=50)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('asset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.itasset')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='auth.user')),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='WorkflowRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_type', models.CharField(choices=[('new_device', 'New Device Request'), ('maintenance', 'Maintenance Request'), ('damage_report', 'Damage Report'), ('loss_report', 'Loss Report')], max_length=50)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('approval_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_requests', to='auth.user')),
                ('asset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.itasset')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workflow_requests', to='auth.user')),
            ],
            options={
                'verbose_name': 'Workflow Request',
                'verbose_name_plural': 'Workflow Requests',
                'ordering': ['-created_at'],
            },
        ),
    ] 