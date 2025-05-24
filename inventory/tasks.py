from django.utils import timezone
from datetime import timedelta
from .models import ITAsset, Notification
from django.contrib.auth.models import User

def check_warranty_expirations():
    """Check for assets with warranty expiring in the next 30 days."""
    thirty_days_from_now = timezone.now() + timedelta(days=30)
    
    # Get assets with warranty expiring soon
    expiring_assets = ITAsset.objects.filter(
        warranty_end_date__lte=thirty_days_from_now,
        warranty_end_date__gt=timezone.now()
    )
    
    for asset in expiring_assets:
        # Create notification for IT department
        Notification.objects.create(
            notification_type='warranty_expiry',
            title='Warranty Expiring Soon',
            message=f'The warranty for {asset.name} (Serial: {asset.serial_number}) will expire on {asset.warranty_end_date.strftime("%Y-%m-%d")}.',
            asset=asset,
            recipient=asset.assigned_to.user if asset.assigned_to and asset.assigned_to.user else None
        )

def check_serial_expirations():
    """Check for assets with serial period expiring in the next 30 days."""
    thirty_days_from_now = timezone.now() + timedelta(days=30)
    
    # Get assets with serial period expiring soon
    expiring_assets = ITAsset.objects.filter(
        serial_expiry_date__lte=thirty_days_from_now,
        serial_expiry_date__gt=timezone.now()
    )
    
    for asset in expiring_assets:
        # Create notification for IT department
        Notification.objects.create(
            notification_type='serial_expiry',
            title='Serial Period Expiring Soon',
            message=f'The serial period for {asset.name} (Serial: {asset.serial_number}) will expire on {asset.serial_expiry_date.strftime("%Y-%m-%d")}.',
            asset=asset,
            recipient=asset.assigned_to.user if asset.assigned_to and asset.assigned_to.user else None
        ) 