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
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'In Maintenance'),
        ('retired', 'Retired'),
    ]

    name = models.CharField(max_length=100, default='Unknown Asset')
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    serial_number = models.CharField(max_length=50, unique=True)
    model = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    purchase_date = models.DateField()
    warranty_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'IT Asset'
        verbose_name_plural = 'IT Assets'
