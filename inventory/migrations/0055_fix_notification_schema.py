from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0054_create_notification_categories'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            BEGIN;
            -- Drop the existing notification table
            DROP TABLE IF EXISTS inventory_notification CASCADE;
            
            -- Recreate the notification table with the correct schema
            CREATE TABLE inventory_notification (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                priority VARCHAR(10) NOT NULL,
                status VARCHAR(10) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP WITH TIME ZONE NULL,
                archived_at TIMESTAMP WITH TIME ZONE NULL,
                expires_at TIMESTAMP WITH TIME ZONE NULL,
                action_url VARCHAR(200) NULL,
                object_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                content_type_id INTEGER NOT NULL,
                employee_profile_id INTEGER NULL
            );
            
            -- Add indexes
            CREATE INDEX inventory_n_status_b440fc_idx ON inventory_notification (status, created_at);
            CREATE INDEX inventory_n_employe_37314b_idx ON inventory_notification (employee_profile_id, status);
            CREATE INDEX inventory_n_content_41af1e_idx ON inventory_notification (content_type_id, object_id);
            
            -- Add foreign key constraints
            ALTER TABLE inventory_notification 
                ADD CONSTRAINT fk_notification_category 
                FOREIGN KEY (category_id) 
                REFERENCES inventory_notificationcategory(id);
                
            ALTER TABLE inventory_notification 
                ADD CONSTRAINT fk_notification_content_type 
                FOREIGN KEY (content_type_id) 
                REFERENCES django_content_type(id);
                
            ALTER TABLE inventory_notification 
                ADD CONSTRAINT fk_notification_employee 
                FOREIGN KEY (employee_profile_id) 
                REFERENCES inventory_employee(id);
            COMMIT;
            """,
            reverse_sql="""
            BEGIN;
            DROP TABLE IF EXISTS inventory_notification CASCADE;
            COMMIT;
            """
        ),
    ] 