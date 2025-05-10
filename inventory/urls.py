from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.home, name='home'),
    
    # Employee URLs
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/update/', views.employee_update, name='employee_update'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('employees/<int:pk>/toggle-status/', views.employee_toggle_status, name='employee_toggle_status'),
    
    # IT Asset URLs
    path('assets/', views.ITAssetListView.as_view(), name='asset_list'),
    path('assets/create/', views.ITAssetCreateView.as_view(), name='asset_create'),
    path('assets/<int:pk>/', views.ITAssetDetailView.as_view(), name='asset_detail'),
    path('assets/<int:pk>/update/', views.ITAssetUpdateView.as_view(), name='asset_update'),
    path('assets/<int:pk>/delete/', views.ITAssetDeleteView.as_view(), name='asset_delete'),
    path('assets/assign/', views.asset_assign, name='asset_assign'),
]
