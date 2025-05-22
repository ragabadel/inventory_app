from django import template
from inventory.models import AssetHistory

register = template.Library()

@register.filter
def action_badge_color(action):
    """
    Returns the appropriate Bootstrap badge color class based on the action type.
    """
    color_map = {
        'received': 'success',
        'assigned': 'primary',
        'returned': 'info',
        'maintenance': 'warning',
        'retired': 'secondary',
    }
    return color_map.get(action, 'secondary') 