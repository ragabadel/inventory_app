# Generated by Django 5.2.1 on 2025-07-18 20:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_outlet'),
    ]

    operations = [
        migrations.AddField(
            model_name='itasset',
            name='outlet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assets', to='inventory.outlet'),
        ),
    ]
