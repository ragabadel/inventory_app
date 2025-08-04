from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0017_alter_itasset_options_objectpermission_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE inventory_itasset DROP CONSTRAINT IF EXISTS inventory_itasset_delivery_letter_code_70216e02_uniq;',
            reverse_sql='ALTER TABLE inventory_itasset ADD CONSTRAINT inventory_itasset_delivery_letter_code_70216e02_uniq UNIQUE (delivery_letter_code);'
        ),
    ]