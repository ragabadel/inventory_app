from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.home, name='home'),
    path('landing/', views.LandingPageView.as_view(), name='landing'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # User Account Management
    path('account/', views.UserAccountView.as_view(), name='user_account'),
    path('account/change-password/', views.change_password, name='change_password'),
    
    # Employee URLs
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    path('employees/<int:pk>/pdf/', views.EmployeePDFView.as_view(), name='employee_pdf'),
    path('employees/<int:pk>/toggle-status/', views.employee_toggle_status, name='employee_toggle_status'),
    path('employees/upload/', views.employee_upload, name='employee_upload'),
    path('employees/download-template/', views.download_employee_template, name='download_employee_template'),
    path('employees/download-data/', views.download_employee_data, name='download_employee_data'),
    
    # IT Asset URLs
    path('assets/', views.ITAssetListView.as_view(), name='asset_list'),
    path('assets/content/', views.AssetListContentView.as_view(), name='asset_list_content'),
    path('assets/<int:pk>/', views.ITAssetDetailView.as_view(), name='asset_detail'),
    path('assets/create/', views.ITAssetCreateView.as_view(), name='asset_create'),
    path('assets/<int:pk>/update/', views.ITAssetUpdateView.as_view(), name='asset_update'),
    path('assets/<int:pk>/delete/', views.ITAssetDeleteView.as_view(), name='asset_delete'),
    path('assets/<int:pk>/receipt/', views.asset_receipt, name='asset_receipt'),
    path('assets/assign/', views.asset_assign, name='asset_assign'),
    path('assets/upload/', views.asset_upload, name='asset_upload'),
    path('assets/download-template/', views.download_asset_template, name='download_asset_template'),
    path('assets/download-data/', views.download_asset_data, name='download_asset_data'),
    path('assets/<int:pk>/history/', views.asset_history, name='asset_history'),
    path('assets/<int:pk>/unassign/', views.asset_unassign, name='asset_unassign'),
    
    # Asset Type URLs
    path('asset-types/', views.AssetTypeListView.as_view(), name='asset_type_list'),
    path('asset-types/create/', views.AssetTypeCreateView.as_view(), name='asset_type_create'),
    path('asset-types/<int:pk>/update/', views.AssetTypeUpdateView.as_view(), name='asset_type_update'),
    path('asset-types/<int:pk>/delete/', views.AssetTypeDeleteView.as_view(), name='asset_type_delete'),
    
    # Owner Company URLs
    path('companies/', views.OwnerCompanyListView.as_view(), name='owner_company_list'),
    path('companies/create/', views.OwnerCompanyCreateView.as_view(), name='owner_company_create'),
    path('companies/<int:pk>/update/', views.OwnerCompanyUpdateView.as_view(), name='owner_company_update'),
    path('companies/<int:pk>/delete/', views.OwnerCompanyDeleteView.as_view(), name='owner_company_delete'),

    # Asset Types
    path('asset-types/', views.asset_type_list, name='asset_type_list'),
    path('asset-types/<int:pk>/', views.asset_type_detail, name='asset_type_detail'),

    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/update/', views.department_update, name='department_update'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),

    # Notification URLs
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<int:pk>/mark-unread/', views.mark_notification_unread, name='mark_notification_unread'),
    path('notifications/<int:pk>/archive/', views.archive_notification, name='archive_notification'),
    path('notifications/<int:pk>/unarchive/', views.unarchive_notification, name='unarchive_notification'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/ajax/', views.get_notifications_ajax, name='get_notifications_ajax'),

    # Device History URLs
    path('devices/<int:pk>/history/', views.device_history, name='device_history'),

    # User Permissions Management
    path('users/permissions/', views.UserPermissionsView.as_view(), name='user_permissions'),

    # Global Asset History
    path('asset-history/', views.global_asset_history, name='global_asset_history'),

    # Reports Dashboard
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/pdf/', views.generate_report_pdf, name='generate_report_pdf'),

    # Database Management URLs (Superuser Only)
    path('database/backup/', views.DatabaseBackupView.as_view(), name='database_backup'),
    path('database/restore/', views.DatabaseRestoreView.as_view(), name='database_restore'),
]
