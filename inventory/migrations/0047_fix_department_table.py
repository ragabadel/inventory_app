from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0046_merge_all_heads'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - Only create if doesn't exist
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename = 'inventory_department'
                ) THEN
                    CREATE TABLE inventory_department (
                        id bigserial PRIMARY KEY,
                        name varchar(100) NOT NULL,
                        description text,
                        created_at timestamp with time zone DEFAULT now(),
                        updated_at timestamp with time zone DEFAULT now()
                    );
                END IF;
            END $$;
            """,
            # Reverse SQL - Do nothing since we don't want to drop the table
            "SELECT 1;"
        ),
    ] 