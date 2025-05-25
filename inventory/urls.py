from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.home, name='home'),
    
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
    path('assets/<int:pk>/history/', views.asset_history, name='asset_history'),
    
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
    
    # Owner Companies
    path('companies/', views.owner_company_list, name='owner_company_list'),
    path('companies/<int:pk>/', views.owner_company_detail, name='owner_company_detail'),
    
    # Asset Types
    path('asset-types/', views.asset_type_list, name='asset_type_list'),
    path('asset-types/<int:pk>/', views.asset_type_detail, name='asset_type_detail'),

    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/update/', views.department_update, name='department_update'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),

    path('devices/<int:pk>/history/', views.device_history, name='device_history'),
]
