from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from inventory.models import Notification, NotificationCategory, Employee, ITAsset

class NotificationService:
    @staticmethod
    def create_notification(title, message, category_name, priority='medium', employee=None, 
                          related_object=None, action_url=None, expires_at=None, send_email=False):
        """
        Creates a notification with the specified parameters.
        
        Args:
            title (str): The notification title
            message (str): The notification message
            category_name (str): Name of the notification category
            priority (str): Priority level (low, medium, high, urgent)
            employee (Employee): Target employee (optional)
            related_object: The related model instance (optional)
            action_url (str): URL for additional action (optional)
            expires_at (datetime): Expiration datetime (optional)
            send_email (bool): Whether to send email notification
        """
        try:
            # Get or create category
            category = NotificationCategory.objects.get(name=category_name)
            
            # Create notification
            notification = Notification.objects.create(
                title=title,
                message=message,
                category=category,
                priority=priority,
                employee_profile=employee,
                action_url=action_url,
                expires_at=expires_at,
                status='unread'
            )
            
            # Set related object if provided
            if related_object:
                notification.content_type = ContentType.objects.get_for_model(related_object)
                notification.object_id = related_object.id
                notification.save()
            
            # Send email if requested
            if send_email and employee and employee.email:
                NotificationService._send_email_notification(notification)
            
            return notification
            
        except NotificationCategory.DoesNotExist:
            raise ValueError(f"Notification category '{category_name}' does not exist")
        except Exception as e:
            raise Exception(f"Failed to create notification: {str(e)}")

    @staticmethod
    def create_device_assignment_notification(asset, employee, action='assigned'):
        """Creates a notification for device assignment/return."""
        if action not in ['assigned', 'returned']:
            raise ValueError("Action must be either 'assigned' or 'returned'")
        
        title = _('Device {action}').format(
            action=_('Assigned') if action == 'assigned' else _('Returned')
        )
        
        message = _('Device {device} has been {action} {to_from} {employee}').format(
            device=asset.name,
            action=_('assigned to') if action == 'assigned' else _('returned from'),
            to_from=_('to') if action == 'assigned' else _('by'),
            employee=employee.get_full_name()
        )
        
        return NotificationService.create_notification(
            title=title,
            message=message,
            category_name='Device Assignment',
            priority='medium',
            employee=employee,
            related_object=asset,
            action_url=asset.get_absolute_url(),
            send_email=True
        )

    @staticmethod
    def create_warranty_notification(asset, days_remaining):
        """Creates a notification for warranty expiration."""
        if days_remaining <= 0:
            title = _('Warranty Expired')
            message = _('The warranty for {device} has expired').format(device=asset.name)
            priority = 'high'
        else:
            title = _('Warranty Expiring Soon')
            message = _('The warranty for {device} will expire in {days} days').format(
                device=asset.name,
                days=days_remaining
            )
            priority = 'medium'
        
        return NotificationService.create_notification(
            title=title,
            message=message,
            category_name='Warranty',
            priority=priority,
            related_object=asset,
            action_url=asset.get_absolute_url()
        )

    @staticmethod
    def create_maintenance_notification(asset, maintenance_type, notes=None):
        """Creates a notification for device maintenance."""
        title = _('Maintenance Required: {device}').format(device=asset.name)
        message = _('Maintenance type: {type}\n{notes}').format(
            type=maintenance_type,
            notes=notes if notes else ''
        )
        
        return NotificationService.create_notification(
            title=title,
            message=message,
            category_name='Maintenance',
            priority='high',
            related_object=asset,
            action_url=asset.get_absolute_url()
        )

    @staticmethod
    def create_system_alert(title, message, priority='medium'):
        """Creates a system-wide notification."""
        return NotificationService.create_notification(
            title=title,
            message=message,
            category_name='System',
            priority=priority
        )

    @staticmethod
    def get_user_notifications(user, status=None, category=None, priority=None):
        """Gets notifications for a specific user with optional filters."""
        queryset = Notification.objects.select_related('category', 'employee_profile', 'content_type')
        
        # Filter by employee profile or system-wide notifications
        if hasattr(user, 'employee_profile') and user.employee_profile:
            queryset = queryset.filter(
                Q(employee_profile=user.employee_profile) |
                Q(employee_profile__isnull=True)
            )
        else:
            queryset = queryset.filter(employee_profile__isnull=True)
        
        # Apply additional filters
        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category__name=category)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('-created_at')

    @staticmethod
    def mark_as_read(notification_ids, user):
        """Marks multiple notifications as read."""
        notifications = NotificationService.get_user_notifications(user).filter(
            id__in=notification_ids,
            status='unread'
        )
        
        for notification in notifications:
            notification.mark_as_read()

    @staticmethod
    def _send_email_notification(notification):
        """Sends an email for the notification."""
        if not notification.employee_profile or not notification.employee_profile.email:
            return
        
        context = {
            'notification': notification,
            'action_url': notification.action_url or '',
        }
        
        html_message = render_to_string('inventory/emails/notification.html', context)
        plain_message = render_to_string('inventory/emails/notification.txt', context)
        
        send_mail(
            subject=notification.title,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.employee_profile.email],
            fail_silently=True
        ) 