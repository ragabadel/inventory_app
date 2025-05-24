from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.home, name='dashboard'),
    path('landing/', views.LandingPageView.as_view(), name='landing_page'),
    
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
    path('assets/<int:pk>/', views.ITAssetDetailView.as_view(), name='asset_detail'),
    path('assets/create/', views.ITAssetCreateView.as_view(), name='asset_create'),
    path('assets/<int:pk>/update/', views.ITAssetUpdateView.as_view(), name='asset_update'),
    path('assets/<int:pk>/delete/', views.ITAssetDeleteView.as_view(), name='asset_delete'),
    path('assets/assign/', views.asset_assign, name='asset_assign'),
    path('assets/upload/', views.asset_upload, name='asset_upload'),
    path('assets/download-template/', views.download_asset_template, name='download_asset_template'),
    path('assets/download-data/', views.download_asset_data, name='download_asset_data'),
    
    # Asset Type URLs
    path('asset-types/', views.AssetTypeListView.as_view(), name='asset_type_list'),
    path('asset-types/create/', views.AssetTypeCreateView.as_view(), name='asset_type_create'),
    path('asset-types/<int:pk>/update/', views.AssetTypeUpdateView.as_view(), name='asset_type_update'),
    path('asset-types/<int:pk>/delete/', views.AssetTypeDeleteView.as_view(), name='asset_type_delete'),
    
    # Owner Company URLs
    path('owner-companies/', views.OwnerCompanyListView.as_view(), name='owner_company_list'),
    path('owner-companies/create/', views.OwnerCompanyCreateView.as_view(), name='owner_company_create'),
    path('owner-companies/<int:pk>/update/', views.OwnerCompanyUpdateView.as_view(), name='owner_company_update'),
    path('owner-companies/<int:pk>/delete/', views.OwnerCompanyDeleteView.as_view(), name='owner_company_delete'),

    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/mark-as-read/', views.NotificationMarkAsReadView.as_view(), name='notification_mark_as_read'),

    # Workflow Requests
    path('requests/', views.WorkflowRequestListView.as_view(), name='workflow_request_list'),
    path('requests/create/', views.WorkflowRequestCreateView.as_view(), name='workflow_request_create'),
    path('requests/<int:pk>/', views.WorkflowRequestDetailView.as_view(), name='workflow_request_detail'),
    path('requests/<int:pk>/approve/', views.WorkflowRequestApproveView.as_view(), name='workflow_request_approve'),

    # Language Preference
    path('language/', views.update_language, name='update_language'),

    # Device and Maintenance Requests
    path('device/request/', views.create_device_request, name='create_device_request'),
    path('asset/<int:asset_id>/maintenance/', views.create_maintenance_request, name='create_maintenance_request'),
    path('asset/<int:asset_id>/damage/', views.report_damaged_device, name='report_damaged_device'),
    path('asset/<int:asset_id>/loss/', views.report_lost_device, name='report_lost_device'),

    # User Management
    path('users/', views.UserManagementView.as_view(), name='user_management'),
    path('users/create/', views.CreateUserView.as_view(), name='create_user'),
    path('users/<int:pk>/edit/', views.EditUserView.as_view(), name='edit_user'),
    path('users/<int:pk>/activate/', views.activate_user, name='activate_user'),
    path('users/<int:pk>/deactivate/', views.deactivate_user, name='deactivate_user'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete_user'),
    path('asset-history/', views.AssetHistoryView.as_view(), name='asset_history'),

    # Department URLs
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
]
