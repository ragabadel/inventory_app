from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0042_fix_postgres_position_column'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL
            """
            BEGIN;
            -- Drop existing foreign key constraint if it exists
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 
                    FROM information_schema.table_constraints 
                    WHERE constraint_name = 'inventory_employee_position_id_fkey'
                    AND table_name = 'inventory_employee'
                ) THEN
                    ALTER TABLE inventory_employee DROP CONSTRAINT inventory_employee_position_id_fkey;
                END IF;
            END $$;

            -- Add the foreign key constraint back with correct reference
            ALTER TABLE inventory_employee
            ADD CONSTRAINT inventory_employee_position_id_fkey
            FOREIGN KEY (position_id)
            REFERENCES inventory_position(id)
            ON DELETE RESTRICT;

            COMMIT;
            """,
            # Reverse SQL - in case we need to rollback
            """
            BEGIN;
            ALTER TABLE inventory_employee DROP CONSTRAINT IF EXISTS inventory_employee_position_id_fkey;
            COMMIT;
            """
        ),
    ] 