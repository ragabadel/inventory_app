from django.core.management.base import BaseCommand
from inventory.models import ITAsset

class Command(BaseCommand):
    help = 'Updates NULL asset names and makes the name field required'

    def handle(self, *args, **options):
        # Update NULL names
        updated = ITAsset.objects.filter(name__isnull=True).update(name='Unknown Asset')
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} assets with NULL names'))
        
        # Verify no NULL names remain
        null_count = ITAsset.objects.filter(name__isnull=True).count()
        if null_count == 0:
            self.stdout.write(self.style.SUCCESS('No NULL names remain in the database'))
        else:
            self.stdout.write(self.style.ERROR(f'Warning: {null_count} assets still have NULL names')) 