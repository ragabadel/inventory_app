from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # Language prefix URL
]

# Add the inventory app URLs with i18n_patterns
urlpatterns += i18n_patterns(
    path('inventory/', include('inventory.urls')),  # Changed from '' to 'inventory/'
    prefix_default_language=False
)

# Add static and media URLs in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 