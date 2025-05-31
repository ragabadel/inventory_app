from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0040_fix_employee_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='position',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='employees',
                to='inventory.position',
                db_column='position_id'
            ),
        ),
    ] 