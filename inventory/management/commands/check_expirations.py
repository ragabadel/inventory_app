from django.core.management.base import BaseCommand
from inventory.tasks import check_warranty_expirations, check_serial_expirations

class Command(BaseCommand):
    help = 'Check for warranty and serial period expirations'

    def handle(self, *args, **options):
        self.stdout.write('Checking warranty expirations...')
        check_warranty_expirations()
        self.stdout.write(self.style.SUCCESS('Warranty expiration check completed'))
        
        self.stdout.write('Checking serial period expirations...')
        check_serial_expirations()
        self.stdout.write(self.style.SUCCESS('Serial period expiration check completed')) 