from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('inventory', '0049_fix_notification_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('icon', models.CharField(help_text='FontAwesome icon class (e.g., fa-bell)', max_length=50, verbose_name='Icon Class')),
                ('color', models.CharField(help_text='Bootstrap color class (e.g., primary, danger)', max_length=20, verbose_name='Color')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Notification Category',
                'verbose_name_plural': 'Notification Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('message', models.TextField(verbose_name='Message')),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10, verbose_name='Priority')),
                ('status', models.CharField(choices=[('unread', 'Unread'), ('read', 'Read'), ('archived', 'Archived')], default='unread', max_length=10, verbose_name='Status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='Read At')),
                ('archived_at', models.DateTimeField(blank=True, null=True, verbose_name='Archived At')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='Expires At')),
                ('is_email_sent', models.BooleanField(default=False, verbose_name='Email Sent')),
                ('action_url', models.CharField(blank=True, max_length=255, verbose_name='Action URL')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='inventory.notificationcategory', verbose_name='Category')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='Content Type')),
                ('employee_profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='inventory.employee', verbose_name='Employee')),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['status', 'created_at'], name='inventory_n_status_b440fc_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['employee_profile', 'status'], name='inventory_n_employe_a440fc_idx'),
        ),
    ] 