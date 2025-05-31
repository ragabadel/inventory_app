from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0041_update_employee_position_field'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - rename column if it exists
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'inventory_employee'
                    AND column_name = 'position'
                ) THEN
                    ALTER TABLE inventory_employee RENAME COLUMN position TO position_id;
                END IF;
            END $$;
            """,
            # Reverse SQL
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'inventory_employee'
                    AND column_name = 'position_id'
                ) THEN
                    ALTER TABLE inventory_employee RENAME COLUMN position_id TO position;
                END IF;
            END $$;
            """
        ),
    ] 