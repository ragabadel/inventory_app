from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Department(models.Model):
    DEPARTMENT_CHOICES = [
        ('warehouse', 'Warehouse'),
        ('hr', 'HR'),
        ('procurement', 'Procurement'),
        ('quality', 'Quality'),
        ('finance', 'Finance'),
        ('production', 'Production'),
        ('maintenance', 'Maintenance'),
        ('osh', 'Occupational Safety and Health'),
        ('it', 'IT'),
    ]

    name = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    @classmethod
    def get_department_choices(cls):
        return cls.DEPARTMENT_CHOICES

    def get_name_display(self):
        return dict(self.DEPARTMENT_CHOICES).get(self.name, self.name)

class Position(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.department.get_name_display()})"

    class Meta:
        ordering = ['department', 'name']

class OwnerCompany(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Owner Company'
        verbose_name_plural = 'Owner Companies'

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True, help_text="Enter employee ID (e.g., EMP001 or ABC123)")
    national_id = models.CharField(max_length=14, unique=True, help_text="Enter the 14-digit national ID number")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name='employees')
    hire_date = models.DateField()
    company = models.ForeignKey(OwnerCompany, on_delete=models.PROTECT, related_name='employees')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

class AssetType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_name']
        verbose_name = 'Asset Type'
        verbose_name_plural = 'Asset Types'

    def __str__(self):
        return self.display_name

class ITAsset(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    ]

    # Basic Information
    name = models.CharField(max_length=100, default='Unknown Asset')
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=50, unique=True)
    model = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    owner = models.ForeignKey(OwnerCompany, on_delete=models.PROTECT)
    purchase_date = models.DateField()
    warranty_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    # Network Information
    mac_address_wifi = models.CharField(max_length=17, blank=True, verbose_name='Wi-Fi MAC Address')
    mac_address_ethernet = models.CharField(max_length=17, blank=True, verbose_name='Ethernet MAC Address')
    ip_address = models.CharField(max_length=15, blank=True, verbose_name='IP Address')

    # Delivery Information
    delivery_letter_code = models.CharField(max_length=50, blank=True)
    receipt_date = models.DateField(null=True, blank=True)

    # Computer Specifications (for laptops and desktops)
    processor = models.CharField(max_length=100, blank=True, null=True)
    ram_size = models.CharField(max_length=50, blank=True, null=True)
    hdd1_capacity = models.CharField(max_length=50, blank=True, null=True, verbose_name='Primary Storage')
    hdd2_capacity = models.CharField(max_length=50, blank=True, null=True, verbose_name='Secondary Storage')
    operating_system = models.CharField(max_length=50, blank=True, null=True)
    os_version = models.CharField(max_length=50, blank=True, null=True)

    # Monitor Specifications
    screen_size = models.CharField(max_length=20, blank=True, null=True)
    resolution = models.CharField(max_length=50, blank=True, null=True)
    refresh_rate = models.CharField(max_length=20, blank=True, null=True)
    panel_type = models.CharField(max_length=50, blank=True, null=True)
    vesa_mount = models.BooleanField(default=False)
    built_in_speakers = models.BooleanField(default=False)

    # Printer Specifications
    printer_type = models.CharField(max_length=50, blank=True, null=True)
    connection_type = models.CharField(max_length=50, blank=True, null=True)
    printer_department = models.CharField(max_length=100, blank=True, null=True)
    printer_responsible = models.CharField(max_length=100, blank=True, null=True)
    paper_size_support = models.CharField(max_length=100, blank=True, null=True)
    duplex_printing = models.BooleanField(default=False)
    toner_cartridge_model = models.CharField(max_length=100, blank=True, null=True)

    # UPS Specifications
    ups_capacity = models.IntegerField(blank=True, null=True, help_text='Capacity in VA')
    ups_battery_count = models.IntegerField(blank=True, null=True, help_text='Number of batteries')
    ups_battery_life = models.IntegerField(blank=True, null=True, help_text='Remaining battery life in months')
    ups_battery_replacement_date = models.DateField(blank=True, null=True)
    ups_manufacturer = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'IT Asset'
        verbose_name_plural = 'IT Assets'

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

class AssetHistory(models.Model):
    ACTION_CHOICES = [
        ('received', 'Received'),
        ('assigned', 'Assigned'),
        ('returned', 'Returned'),
        ('maintenance', 'Maintenance'),
        ('retired', 'Retired'),
    ]

    asset = models.ForeignKey(ITAsset, on_delete=models.CASCADE, related_name='asset_history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Asset History'
        verbose_name_plural = 'Asset Histories'

    def __str__(self):
        return f"{self.asset.name} - {self.get_action_display()} ({self.date.strftime('%Y-%m-%d')})"

class DeviceHistory(models.Model):
    EVENT_TYPES = [
        ('assignment', _('Assignment')),
        ('maintenance', _('Maintenance')),
        ('status_change', _('Status Change')),
        ('other', _('Other')),
    ]

    device = models.ForeignKey('ITAsset', on_delete=models.CASCADE, related_name='device_history')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Device History')
        verbose_name_plural = _('Device Histories')

    def __str__(self):
        return f"{self.device.name} - {self.get_event_type_display()} - {self.timestamp}"
