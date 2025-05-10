import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_app.settings')
django.setup()

from inventory.models import ITAsset

def update_asset_names():
    # Update NULL names
    updated = ITAsset.objects.filter(name__isnull=True).update(name='Unknown Asset')
    print(f'Updated {updated} assets with NULL names')
    
    # Verify no NULL names remain
    null_count = ITAsset.objects.filter(name__isnull=True).count()
    if null_count == 0:
        print('No NULL names remain in the database')
    else:
        print(f'Warning: {null_count} assets still have NULL names')

if __name__ == '__main__':
    update_asset_names() 