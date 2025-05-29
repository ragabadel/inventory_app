from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
from inventory.models import ITAsset, NotificationCategory, Notification

class Command(BaseCommand):
    help = 'Check asset warranties and create notifications for expiring and expired warranties'

    def handle(self, *args, **options):
        self.check_warranty_expiry()
        self.check_expired_warranties()
        self.stdout.write(self.style.SUCCESS('Successfully checked all warranties'))

    def check_warranty_expiry(self):
        """Check for warranties expiring in the next 30 days"""
        today = timezone.now().date()
        thirty_days_later = today + timedelta(days=30)

        # Get warranty category and content type
        try:
            warranty_category = NotificationCategory.objects.get(name='Warranty')
            asset_content_type = ContentType.objects.get_for_model(ITAsset)
        except NotificationCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR('Warranty notification category not found'))
            return
        except ContentType.DoesNotExist:
            self.stdout.write(self.style.ERROR('ITAsset content type not found'))
            return

        # Find assets with warranties expiring soon
        expiring_assets = ITAsset.objects.filter(
            warranty_expiry__gt=today,
            warranty_expiry__lte=thirty_days_later
        )

        # Filter out assets that already have recent notifications
        for asset in expiring_assets:
            recent_notification = Notification.objects.filter(
                content_type=asset_content_type,
                object_id=asset.id,
                category=warranty_category,
                created_at__gte=today - timedelta(days=7)  # Don't notify if already notified in the last 7 days
            ).exists()

            if not recent_notification:
                days_remaining = (asset.warranty_expiry - today).days
                
                # Create notification
                Notification.objects.create(
                    title=f'Warranty Expiring Soon: {asset.name}',
                    message=f'The warranty for {asset.name} (SN: {asset.serial_number}) will expire in {days_remaining} days on {asset.warranty_expiry}.',
                    priority='medium',
                    employee_profile=asset.assigned_to,
                    content_type=asset_content_type,
                    object_id=asset.id,
                    category=warranty_category
                )
                
                self.stdout.write(self.style.SUCCESS(f'Created expiring warranty notification for {asset.name}'))

    def check_expired_warranties(self):
        """Check for warranties that have already expired"""
        today = timezone.now().date()

        # Get warranty category and content type
        try:
            warranty_category = NotificationCategory.objects.get(name='Warranty')
            asset_content_type = ContentType.objects.get_for_model(ITAsset)
        except NotificationCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR('Warranty notification category not found'))
            return
        except ContentType.DoesNotExist:
            self.stdout.write(self.style.ERROR('ITAsset content type not found'))
            return

        # Find assets with expired warranties
        expired_assets = ITAsset.objects.filter(
            warranty_expiry__lt=today
        )

        # Filter out assets that already have recent notifications
        for asset in expired_assets:
            recent_notification = Notification.objects.filter(
                content_type=asset_content_type,
                object_id=asset.id,
                category=warranty_category,
                created_at__gte=today - timedelta(days=30)  # Don't notify if already notified in the last 30 days
            ).exists()

            if not recent_notification:
                days_expired = (today - asset.warranty_expiry).days
                
                # Create notification
                Notification.objects.create(
                    title=f'Warranty Expired: {asset.name}',
                    message=f'The warranty for {asset.name} (SN: {asset.serial_number}) expired {days_expired} days ago on {asset.warranty_expiry}.',
                    priority='high',
                    employee_profile=asset.assigned_to,
                    content_type=asset_content_type,
                    object_id=asset.id,
                    category=warranty_category
                )
                
                self.stdout.write(self.style.SUCCESS(f'Created expired warranty notification for {asset.name}')) 