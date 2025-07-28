from django.shortcuts import render
from django.utils.translation import gettext as _
from django.contrib import messages

def handler403(request, exception=None):
    """Custom 403 error handler"""
    messages.error(request, _("You don't have permission to access this page."))
    return render(request, '403.html', status=403) 