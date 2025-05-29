from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from inventory.models import ITAsset, Notification

class Command(BaseCommand):
    help = 'Check for various notification conditions and create notifications'

    def handle(self, *args, **options):
        self.check_warranty_expiry()
        self.check_serial_expiry()
        self.stdout.write(self.style.SUCCESS('Successfully checked all notifications'))

    def check_warranty_expiry(self):
        today = timezone.now().date()
        thirty_days_later = today + timedelta(days=30)

        # Check for warranties expiring in the next 30 days
        expiring_assets = ITAsset.objects.filter(
            warranty_expiry__gt=today,
            warranty_expiry__lte=thirty_days_later
        ).exclude(
            notifications__notification_type='warranty_expiring',
            notifications__created_at__gte=today - timedelta(days=7)  # Don't notify if already notified in the last 7 days
        )

        for asset in expiring_assets:
            days_remaining = (asset.warranty_expiry - today).days
            Notification.objects.create(
                title=f'Warranty Expiring Soon: {asset.name}',
                message=f'The warranty for {asset.name} (SN: {asset.serial_number}) will expire in {days_remaining} days on {asset.warranty_expiry}.',
                notification_type='warranty_expiring',
                priority='medium',
                asset=asset,
                employee_profile=asset.assigned_to
            )

        # Check for expired warranties
        expired_assets = ITAsset.objects.filter(
            warranty_expiry__lt=today
        ).exclude(
            notifications__notification_type='warranty_expired',
            notifications__created_at__gte=today - timedelta(days=30)  # Don't notify if already notified in the last 30 days
        )

        for asset in expired_assets:
            days_expired = (today - asset.warranty_expiry).days
            Notification.objects.create(
                title=f'Warranty Expired: {asset.name}',
                message=f'The warranty for {asset.name} (SN: {asset.serial_number}) has expired {days_expired} days ago on {asset.warranty_expiry}.',
                notification_type='warranty_expired',
                priority='high',
                asset=asset,
                employee_profile=asset.assigned_to
            )

    def check_serial_expiry(self):
        # This is a placeholder for serial number expiry logic
        # You'll need to define what constitutes a serial number expiry in your system
        pass 