from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fixes phone number data in the Employee table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # First, make the column nullable
            cursor.execute("""
                ALTER TABLE inventory_employee 
                ALTER COLUMN phone_number DROP NOT NULL;
            """)
            
            # Update NULL values to empty string
            cursor.execute("""
                UPDATE inventory_employee 
                SET phone_number = '' 
                WHERE phone_number IS NULL;
            """)
            
            # Add NOT NULL constraint back
            cursor.execute("""
                ALTER TABLE inventory_employee 
                ALTER COLUMN phone_number SET NOT NULL;
            """)
            
            # Set default value
            cursor.execute("""
                ALTER TABLE inventory_employee 
                ALTER COLUMN phone_number SET DEFAULT '';
            """)

        self.stdout.write(self.style.SUCCESS('Successfully fixed phone number data')) 