from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fixes phone number data in the Employee table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # First, make sure any NULL values are converted to empty strings
            cursor.execute("""
                UPDATE inventory_employee 
                SET phone_number = '' 
                WHERE phone_number IS NULL;
            """)
            
            # Create a temporary table with the correct structure
            cursor.execute("""
                CREATE TABLE inventory_employee_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id VARCHAR(20) NOT NULL UNIQUE,
                    national_id VARCHAR(14) NOT NULL UNIQUE,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    email VARCHAR(254) NOT NULL UNIQUE,
                    phone_number VARCHAR(17) NOT NULL DEFAULT '',
                    hire_date DATE NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    department_id INTEGER NOT NULL REFERENCES inventory_department(id),
                    position_id INTEGER NOT NULL REFERENCES inventory_position(id),
                    company_id INTEGER NOT NULL REFERENCES inventory_ownercompany(id),
                    user_id INTEGER REFERENCES auth_user(id)
                );
            """)
            
            # Copy data to the new table
            cursor.execute("""
                INSERT INTO inventory_employee_new 
                SELECT * FROM inventory_employee;
            """)
            
            # Drop the old table
            cursor.execute("""
                DROP TABLE inventory_employee;
            """)
            
            # Rename the new table
            cursor.execute("""
                ALTER TABLE inventory_employee_new 
                RENAME TO inventory_employee;
            """)

        self.stdout.write(self.style.SUCCESS('Successfully fixed phone number data')) 