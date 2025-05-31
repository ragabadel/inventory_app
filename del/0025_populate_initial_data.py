from django.db import migrations

def create_initial_data(apps, schema_editor):
    AssetType = apps.get_model('inventory', 'AssetType')
    OwnerCompany = apps.get_model('inventory', 'OwnerCompany')

    # Create initial asset types
    asset_types = [
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('monitor', 'Monitor'),
        ('phone', 'Phone'),
        ('tablet', 'Tablet'),
        ('printer', 'Printer'),
        ('ups', 'UPS Device'),
        ('other', 'Other'),
    ]

    for name, display_name in asset_types:
        AssetType.objects.get_or_create(
            name=name,
            defaults={'display_name': display_name}
        )

    # Create initial owner companies
    owner_companies = [
        ('AMAN', 'Aman'),
        ('CTP', 'CTP'),
        ('MISR_ASSIST', 'Misr Assist'),
    ]

    for code, name in owner_companies:
        OwnerCompany.objects.get_or_create(
            code=code,
            defaults={'name': name}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0024_alter_itasset_options_remove_itasset_connection_type_and_more'),
    ]

    operations = [
        migrations.RunPython(create_initial_data),
    ] 