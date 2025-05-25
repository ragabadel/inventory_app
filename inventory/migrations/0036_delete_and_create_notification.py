from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0035_update_phone_number_field'),
    ]

    operations = [
        migrations.RunSQL(
            # First, drop the existing table if it exists
            "DROP TABLE IF EXISTS inventory_notification CASCADE;",
            # No reverse SQL needed since we're recreating the table
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('notification_type', models.CharField(
                    choices=[
                        ('warranty_expired', 'Warranty Expired'),
                        ('warranty_expiring', 'Warranty Expiring Soon'),
                        ('license_expired', 'License Expired'),
                        ('license_expiring', 'License Expiring Soon'),
                        ('maintenance_complete', 'Maintenance Complete')
                    ],
                    max_length=50
                )),
                ('status', models.CharField(
                    choices=[('unread', 'Unread'), ('read', 'Read'), ('archived', 'Archived')],
                    default='unread',
                    max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('is_email_sent', models.BooleanField(default=False)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='inventory.itasset')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['notification_type', 'status', 'created_at'], name='notification_type_status_idx'),
                    models.Index(fields=['asset', 'notification_type'], name='notification_asset_type_idx'),
                ],
            },
        ),
    ] 