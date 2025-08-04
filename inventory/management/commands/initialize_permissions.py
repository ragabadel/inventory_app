from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from inventory.models import ITAsset

class Command(BaseCommand):
    help = 'Initialize custom permissions for the inventory app'

    def handle(self, *args, **options):
        # Get content type for ITAsset model
        content_type = ContentType.objects.get_for_model(ITAsset)

        # Create custom permissions
        permissions = [
            ('view_sensitive_data', 'Can view sensitive asset data'),
            ('export_asset_data', 'Can export asset data'),
            ('bulk_update_assets', 'Can perform bulk updates'),
            ('approve_asset_changes', 'Can approve asset changes'),
            ('can_backup_database', 'Can backup database'),
        ]

        for codename, name in permissions:
            Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type,
            )

        self.stdout.write(self.style.SUCCESS('Successfully created custom permissions'))