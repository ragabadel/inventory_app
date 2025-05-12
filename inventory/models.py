from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator

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

class Employee(models.Model):
    COMPANY_CHOICES = [
        ('ACD', 'ACD'),
        ('CTP', 'CTP'),
    ]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    national_id = models.CharField(max_length=14, unique=True, help_text="Enter the 14-digit national ID number")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    company = models.CharField(max_length=3, choices=COMPANY_CHOICES, default='ACD')
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

class ITAsset(models.Model):
    ASSET_TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('monitor', 'Monitor'),
        ('phone', 'Phone'),
        ('tablet', 'Tablet'),
        ('printer', 'Printer'),
        ('ups', 'UPS Device'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'In Maintenance'),
        ('retired', 'Retired'),
    ]

    OWNER_CHOICES = [
        ('AMAN', 'Aman'),
        ('CTP', 'CTP'),
        ('MISR_ASSIST', 'Misr Assist'),
    ]

    PRINTER_TYPE_CHOICES = [
        ('laser', 'Laser'),
        ('inkjet', 'Inkjet'),
        ('dot_matrix', 'Dot Matrix'),
        ('thermal', 'Thermal'),
        ('3d', '3D Printer'),
    ]

    CONNECTION_TYPE_CHOICES = [
        ('usb', 'USB'),
        ('network', 'Network'),
        ('wireless', 'Wireless'),
        ('bluetooth', 'Bluetooth'),
    ]

    # Basic Information
    name = models.CharField(max_length=100, default='Unknown Asset')
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    serial_number = models.CharField(max_length=50, unique=True)
    model = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    owner = models.CharField(max_length=20, choices=OWNER_CHOICES, default='CTP')
    purchase_date = models.DateField()
    warranty_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    notes = models.TextField(blank=True)

    # Network Information
    mac_address_wifi = models.CharField(max_length=17, null=True, blank=True, help_text="Format: XX:XX:XX:XX:XX:XX")
    mac_address_ethernet = models.CharField(max_length=17, null=True, blank=True, help_text="Format: XX:XX:XX:XX:XX:XX")
    ip_address = models.GenericIPAddressField(null=True, blank=True, protocol='IPv4')

    # Assignment Information
    delivery_letter_code = models.CharField(max_length=50, null=True, blank=True)
    receipt_date = models.DateField(null=True, blank=True)

    # Computer Specifications
    processor = models.CharField(max_length=100, null=True, blank=True)
    ram_size = models.CharField(max_length=50, null=True, blank=True)
    hdd1_capacity = models.CharField(max_length=50, null=True, blank=True, help_text="Primary Storage")
    hdd2_capacity = models.CharField(max_length=50, null=True, blank=True, help_text="Secondary Storage")
    operating_system = models.CharField(max_length=50, null=True, blank=True)
    os_version = models.CharField(max_length=50, null=True, blank=True)

    # Printer Specifications
    printer_type = models.CharField(max_length=20, choices=PRINTER_TYPE_CHOICES, null=True, blank=True)
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPE_CHOICES, null=True, blank=True)
    printer_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='printers')
    printer_responsible = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='responsible_printers')
    last_maintenance_date = models.DateField(null=True, blank=True)
    toner_cartridge_model = models.CharField(max_length=100, null=True, blank=True)
    paper_size_support = models.CharField(max_length=100, null=True, blank=True, help_text="e.g., A4, A3, Legal")
    duplex_printing = models.BooleanField(default=False)

    # UPS Specific Fields
    ups_capacity = models.IntegerField(null=True, blank=True, help_text="Capacity in VA")
    ups_battery_count = models.IntegerField(null=True, blank=True, help_text="Number of batteries")
    ups_battery_life = models.IntegerField(null=True, blank=True, help_text="Remaining battery life in months")
    ups_battery_replacement_date = models.DateField(null=True, blank=True)
    ups_manufacturer = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'IT Asset'
        verbose_name_plural = 'IT Assets'
