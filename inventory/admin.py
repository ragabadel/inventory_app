from django.contrib import admin
from .models import Employee, ITAsset, Department, Position

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

@admin.register(ITAsset)
class ITAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_type', 'serial_number', 'status', 'assigned_to', 'purchase_date')
    list_filter = ('asset_type', 'status', 'manufacturer')
    search_fields = ('name', 'serial_number', 'model', 'manufacturer')
    ordering = ('-created_at',)
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
