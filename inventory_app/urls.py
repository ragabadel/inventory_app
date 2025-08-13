"""
URL configuration for inventory_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from inventory.views import SuperUserRegistrationView, LandingPageView
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from inventory.services.permission_service import PermissionService
from django.urls import reverse_lazy

def redirect_to_default_language(request):
    """Redirect root URL to default language URL"""
    return redirect('/en/')

class CustomLoginView(LoginView):
    def get_success_url(self):
        """Return the URL to redirect to after successful login."""
        next_url = self.request.GET.get('next')
        if next_url:
            # Ensure the next URL has the language prefix
            if not next_url.startswith(f'/{self.request.LANGUAGE_CODE}/'):
                next_url = f'/{self.request.LANGUAGE_CODE}{next_url}'
            return next_url
        return reverse_lazy('inventory:home')

    def dispatch(self, request, *args, **kwargs):
        # If user is already authenticated
        if self.request.user.is_authenticated:
            # If session is invalid, log out to avoid redirect loops
            try:
                if not PermissionService.validate_session(request):
                    logout(request)
                else:
                    return redirect(self.get_success_url())
            except Exception:
                logout(request)
        return super().dispatch(request, *args, **kwargs)

urlpatterns = [
    path('', redirect_to_default_language),  # Redirect root to default language
    path('i18n/', include('django.conf.urls.i18n')),  # Language prefix URL
]

urlpatterns += i18n_patterns(
    path('', LandingPageView.as_view(), name='landing'),  # Landing page
    path('admin/', admin.site.urls),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('accounts/login/', CustomLoginView.as_view(
        template_name='registration/login.html',
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
        next_page='landing'
    ), name='logout'),
    path('accounts/register/', SuperUserRegistrationView.as_view(), name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
)

# Error handlers
handler403 = 'inventory.handlers.handler403'
