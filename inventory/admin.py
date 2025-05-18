from django.contrib import admin
from .models import Employee, ITAsset, Department, Position, AssetType, OwnerCompany

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('get_name_display', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'description', 'created_at', 'updated_at')
    list_filter = ('department',)
    search_fields = ('name', 'description')
    ordering = ('department', 'name')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'email', 'department', 'position', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email', 'position')
    ordering = ('last_name', 'first_name')
    fieldsets = (
        ('Personal Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Employment Information', {
            'fields': ('department', 'position', 'hire_date', 'is_active')
        }),
        ('Location Information', {
            'fields': ('office_location', 'desk_number')
        }),
        ('System Access', {
            'fields': ('system_username', 'system_password')
        }),
    )

@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name')
    search_fields = ('name', 'display_name')
    ordering = ('display_name',)

@admin.register(OwnerCompany)
class OwnerCompanyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('name',)

@admin.register(ITAsset)
class ITAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_type', 'serial_number', 'owner', 'status', 'assigned_to')
    list_filter = ('asset_type', 'owner', 'status')
    search_fields = ('name', 'serial_number', 'model', 'manufacturer')
    ordering = ('name',)
    fieldsets = (
        ('Asset Information', {
            'fields': ('name', 'asset_type', 'serial_number', 'model', 'manufacturer')
        }),
        ('Assignment Information', {
            'fields': ('status', 'assigned_to')
        }),
        ('Purchase Information', {
            'fields': ('purchase_date', 'warranty_expiry')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )
