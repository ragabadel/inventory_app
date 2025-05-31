from django.core.management.base import BaseCommand
from django.utils import timezone
from inventory.models import Notification

class Command(BaseCommand):
    help = 'Cleans up expired notifications and archives old ones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days after which to archive read notifications'
        )
        parser.add_argument(
            '--delete-expired',
            action='store_true',
            help='Delete expired notifications instead of archiving them'
        )

    def handle(self, *args, **options):
        now = timezone.now()
        days = options['days']
        delete_expired = options['delete_expired']
        archive_before = now - timezone.timedelta(days=days)

        # Handle expired notifications
        expired_notifications = Notification.objects.filter(
            expires_at__lt=now,
            status__in=['unread', 'read']
        )
        
        if delete_expired:
            count = expired_notifications.count()
            expired_notifications.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {count} expired notifications')
            )
        else:
            count = expired_notifications.update(
                status='archived',
                archived_at=now
            )
            self.stdout.write(
                self.style.SUCCESS(f'Archived {count} expired notifications')
            )

        # Archive old read notifications
        old_notifications = Notification.objects.filter(
            status='read',
            read_at__lt=archive_before
        )
        
        count = old_notifications.update(
            status='archived',
            archived_at=now
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Archived {count} notifications older than {days} days'
            )
        ) 