from django.core.management.base import BaseCommand
from django.core.management import call_command
import json
import os

class Command(BaseCommand):
    help = 'Safely restore database from a JSON backup file, skipping problematic permissions'

    def add_arguments(self, parser):
        parser.add_argument('backup_file', type=str, help='Path to the backup JSON file')

    def clean_json_content(self, content):
        """Clean and validate JSON content."""
        # Remove any trailing commas
        content = content.replace(',]', ']').replace(',}', '}')
        # Remove any trailing whitespace
        content = content.strip()
        # Ensure the content ends with a proper JSON ending
        if not content.endswith(']'):
            content = content.rsplit('},', 1)[0] + '}]'
        return content

    def process_entry(self, entry):
        """Process a single entry to handle foreign key relationships."""
        if entry['model'] == 'inventory.employee':
            # Set user_id to null for employees
            entry['fields']['user'] = None
        elif entry['model'] == 'inventory.assethistory':
            # Set created_by to null for asset history
            entry['fields']['created_by'] = None
        elif entry['model'] == 'inventory.devicehistory':
            # Set user to null for device history
            entry['fields']['user'] = None
        elif entry['model'] == 'inventory.notification':
            # Handle notification user references
            entry['fields']['user'] = None
        return entry

    def filter_and_sort_data(self, data):
        """Filter out auth-related entries and sort by dependencies."""
        # Skip these models entirely
        skip_models = {
            'auth.permission',
            'auth.group',
            'auth.group_permissions',
            'auth.user_groups',
            'auth.user_user_permissions',
            'auth.user',
            'contenttypes.contenttype',
            'sessions.session',
            'admin.logentry'
        }

        # Define the order of models for proper dependency handling
        model_order = [
            'inventory.ownercompany',
            'inventory.department',
            'inventory.position',
            'inventory.notificationcategory',
            'inventory.employee',
            'inventory.assettype',
            'inventory.itasset',
            'inventory.assethistory',
            'inventory.notification',
            'inventory.devicehistory'
        ]

        # Filter out skipped models and process each entry
        filtered_data = [
            self.process_entry(entry)
            for entry in data
            if entry['model'] not in skip_models
        ]

        # Sort data based on model order
        sorted_data = []
        for model in model_order:
            model_data = [entry for entry in filtered_data if entry['model'] == model]
            sorted_data.extend(model_data)

        # Add any remaining models that weren't in our explicit ordering
        remaining_data = [entry for entry in filtered_data if entry['model'] not in model_order]
        sorted_data.extend(remaining_data)

        return sorted_data

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        
        if not os.path.exists(backup_file):
            self.stdout.write(self.style.ERROR(f'Backup file not found: {backup_file}'))
            return

        try:
            # Read and clean the backup file
            with open(backup_file, 'r', encoding='utf-8') as f:
                content = f.read()
                cleaned_content = self.clean_json_content(content)
                data = json.loads(cleaned_content)

            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(data)} records from backup'))

            # Filter and sort the data
            filtered_data = self.filter_and_sort_data(data)
            self.stdout.write(self.style.SUCCESS(f'Filtered to {len(filtered_data)} records'))

            # Create a temporary file with filtered data
            temp_file = os.path.splitext(backup_file)[0] + '_filtered.json'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, indent=2, ensure_ascii=False)

            try:
                # Load the filtered data
                self.stdout.write(self.style.SUCCESS(f'Loading data from {temp_file}'))
                call_command('loaddata', temp_file, verbosity=1)
                self.stdout.write(self.style.SUCCESS('Successfully restored database'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error during restore: {str(e)}'))
                # Keep the filtered file for inspection in case of error
                self.stdout.write(self.style.WARNING(f'Filtered backup saved to: {temp_file}'))
            else:
                # Only remove the file if successful
                if os.path.exists(temp_file):
                    os.remove(temp_file)

        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'JSON decode error: {str(e)}'))
            # Print the problematic lines around the error
            lines = content.split('\n')
            error_line = e.lineno
            start_line = max(0, error_line - 5)
            end_line = min(len(lines), error_line + 5)
            self.stdout.write('\nProblematic section:')
            for i in range(start_line, end_line):
                prefix = '-> ' if i + 1 == error_line else '   '
                self.stdout.write(f'{prefix}{i+1}: {lines[i]}') 