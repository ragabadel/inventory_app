from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Employee, ITAsset, Department, OwnerCompany

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class SuperUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email')})
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('First Name')})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Last Name')})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Username')
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Password')
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Confirm Password')
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_superuser = True
        user.is_staff = True
        if commit:
            user.save()
        return user

class EmployeeForm(forms.ModelForm):
    """Form for creating and updating Employee records."""
    
    class Meta:
        model = Employee
        fields = [
            'employee_id',
            'national_id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'department',
            'position',
            'hire_date',
            'company',
            'is_active',
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter employee ID (e.g., EMP001)',
                'pattern': '^EMP\d{3}$',
                'title': 'Employee ID must be in the format EMP001'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter 14-digit national ID',
                'pattern': '^\d{14}$',
                'title': 'National ID must be exactly 14 digits'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number (e.g., +201234567890)',
                'pattern': '^\+?1?\d{9,15}$',
                'title': 'Phone number must be in international format (e.g., +201234567890)'
            }),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Enter employee's role or title",
                'required': 'required'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'title': 'Check if employee is currently working, uncheck if they have left'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
            if field.required or field_name == 'position':  # Make position required
                field.widget.attrs['required'] = 'required'
        
        # Update department choices
        self.fields['department'].queryset = Department.objects.all().order_by('name')
        self.fields['department'].empty_label = "Select Department"
        
        # Update company choices
        self.fields['company'].queryset = OwnerCompany.objects.all().order_by('name')
        self.fields['company'].empty_label = "Select Company"
        
        # Add help text for national ID
        self.fields['national_id'].help_text = "Enter the 14-digit national ID number"
        
        # Add help text for employee ID
        self.fields['employee_id'].help_text = "Enter employee ID (letters and numbers only)"
        self.fields['employee_id'].widget.attrs.update({
            'pattern': '^[A-Za-z0-9]+$',
            'title': 'Employee ID must contain only letters and numbers'
        })

        # Update position field
        self.fields['position'].required = True
        self.fields['position'].help_text = "Employee's role or title within the department"

        # Update is_active field
        self.fields['is_active'].help_text = "Indicates if the employee is currently working (checked) or has left work (unchecked)"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Employee.objects.exclude(pk=self.instance.pk if self.instance else None).filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if not employee_id:
            raise forms.ValidationError('Employee ID is required.')
        if not employee_id.isalnum():
            raise forms.ValidationError('Employee ID must contain only letters and numbers.')
        if Employee.objects.exclude(pk=self.instance.pk if self.instance else None).filter(employee_id=employee_id).exists():
            raise forms.ValidationError('This employee ID is already in use.')
        return employee_id

    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if not national_id.isdigit() or len(national_id) != 14:
            raise forms.ValidationError('National ID must be exactly 14 digits.')
        if Employee.objects.exclude(pk=self.instance.pk if self.instance else None).filter(national_id=national_id).exists():
            raise forms.ValidationError('This national ID is already in use.')
        return national_id

    def clean_department(self):
        department = self.cleaned_data.get('department')
        if not department:
            raise forms.ValidationError('Please select a department.')
        return department

    def clean_company(self):
        company = self.cleaned_data.get('company')
        if not company:
            raise forms.ValidationError('Please select a company.')
        return company

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Remove any whitespace
            phone_number = phone_number.strip()
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
        return phone_number or ''  # Return empty string if empty or None

class ITAssetForm(forms.ModelForm):
    """Form for creating and updating ITAsset records."""
    
    class Meta:
        model = ITAsset
        fields = [
            # Basic Information
            'name',
            'asset_type',
            'serial_number',
            'model',
            'manufacturer',
            'owner',
            'purchase_date',
            'warranty_expiry',
            'status',
            'assigned_to',
            'notes',
            
            # Network Information
            'mac_address_wifi',
            'mac_address_ethernet',
            'ip_address',
            'delivery_letter_code',
            'receipt_date',
            
            # Computer Specifications
            'processor',
            'ram_size',
            'hdd1_capacity',
            'hdd2_capacity',
            'operating_system',
            'os_version',
            
            # Monitor Specifications
            'screen_size',
            'resolution',
            'refresh_rate',
            'panel_type',
            'vesa_mount',
            'built_in_speakers',
            
            # Printer Specifications
            'printer_type',
            'connection_type',
            'printer_department',
            'printer_responsible',
            'paper_size_support',
            'duplex_printing',
            'toner_cartridge_model',
            
            # UPS Specifications
            'ups_capacity',
            'ups_battery_count',
            'ups_battery_life',
            'ups_battery_replacement_date',
            'ups_manufacturer',
        ]
        widgets = {
            # Basic Information
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_type': forms.Select(attrs={'class': 'form-select'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # Network Information
            'mac_address_wifi': forms.TextInput(attrs={'class': 'form-control'}),
            'mac_address_ethernet': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_letter_code': forms.TextInput(attrs={'class': 'form-control'}),
            'receipt_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            
            # Computer Specifications
            'processor': forms.TextInput(attrs={'class': 'form-control'}),
            'ram_size': forms.TextInput(attrs={'class': 'form-control'}),
            'hdd1_capacity': forms.TextInput(attrs={'class': 'form-control'}),
            'hdd2_capacity': forms.TextInput(attrs={'class': 'form-control'}),
            'operating_system': forms.TextInput(attrs={'class': 'form-control'}),
            'os_version': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Monitor Specifications
            'screen_size': forms.TextInput(attrs={'class': 'form-control'}),
            'resolution': forms.TextInput(attrs={'class': 'form-control'}),
            'refresh_rate': forms.TextInput(attrs={'class': 'form-control'}),
            'panel_type': forms.TextInput(attrs={'class': 'form-control'}),
            'vesa_mount': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'built_in_speakers': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            # Printer Specifications
            'printer_type': forms.TextInput(attrs={'class': 'form-control'}),
            'connection_type': forms.TextInput(attrs={'class': 'form-control'}),
            'printer_department': forms.TextInput(attrs={'class': 'form-control'}),
            'printer_responsible': forms.TextInput(attrs={'class': 'form-control'}),
            'paper_size_support': forms.TextInput(attrs={'class': 'form-control'}),
            'duplex_printing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'toner_cartridge_model': forms.TextInput(attrs={'class': 'form-control'}),
            
            # UPS Specifications
            'ups_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'ups_battery_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'ups_battery_life': forms.NumberInput(attrs={'class': 'form-control'}),
            'ups_battery_replacement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ups_manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data