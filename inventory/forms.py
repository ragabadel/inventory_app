from django import forms
from .models import Employee, ITAsset, Department

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
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter employee ID'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 14-digit national ID'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter position'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'
        
        # Update department choices
        self.fields['department'].queryset = Department.objects.all().order_by('name')
        self.fields['department'].empty_label = "Select Department"
        self.fields['department'].label_from_instance = lambda obj: obj.get_name_display()
        
        # Update company choices
        self.fields['company'].empty_label = "Select Company"
        
        # Add help text for national ID
        self.fields['national_id'].help_text = "Enter the 14-digit national ID number"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Employee.objects.exclude(pk=self.instance.pk if self.instance else None).filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
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

class ITAssetForm(forms.ModelForm):
    """Form for creating and updating ITAsset records."""
    
    class Meta:
        model = ITAsset
        fields = [
            'name', 'asset_type', 'serial_number', 'model', 'manufacturer',
            'owner', 'purchase_date', 'warranty_expiry', 'status',
            'assigned_to', 'notes',
            # Network Information
            'mac_address_wifi', 'mac_address_ethernet', 'ip_address',
            # Assignment Information
            'delivery_letter_code', 'receipt_date',
            # Computer Specifications
            'processor', 'ram_size', 'hdd1_capacity', 'hdd2_capacity',
            'operating_system', 'os_version',
            # Printer Specifications
            'printer_type', 'connection_type', 'printer_department',
            'printer_responsible', 'last_maintenance_date',
            'toner_cartridge_model', 'paper_size_support', 'duplex_printing',
            # UPS fields
            'ups_capacity', 'ups_battery_count', 'ups_battery_life',
            'ups_battery_replacement_date', 'ups_manufacturer'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_type': forms.Select(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'owner': forms.Select(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            # Network Information
            'mac_address_wifi': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XX:XX:XX:XX:XX:XX',
                'pattern': '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
            }),
            'mac_address_ethernet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XX:XX:XX:XX:XX:XX',
                'pattern': '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
            }),
            'ip_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXX.XXX.XXX.XXX'
            }),
            # Assignment Information
            'delivery_letter_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter delivery letter code'
            }),
            'receipt_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            # Computer Specifications
            'processor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Intel Core i7-1165G7'}),
            'ram_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 16GB DDR4'}),
            'hdd1_capacity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 512GB SSD'}),
            'hdd2_capacity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1TB HDD'}),
            'operating_system': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Windows 10'}),
            'os_version': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 21H2'}),
            # Printer Specifications
            'printer_type': forms.Select(attrs={'class': 'form-control'}),
            'connection_type': forms.Select(attrs={'class': 'form-control'}),
            'printer_department': forms.Select(attrs={'class': 'form-control'}),
            'printer_responsible': forms.Select(attrs={'class': 'form-control'}),
            'last_maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'toner_cartridge_model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., HP 26A'
            }),
            'paper_size_support': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., A4, A3, Legal'
            }),
            'duplex_printing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # UPS fields
            'ups_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'ups_battery_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'ups_battery_life': forms.NumberInput(attrs={'class': 'form-control'}),
            'ups_battery_replacement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ups_manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'
        
        # Set the choices for the owner field
        self.fields['owner'].choices = ITAsset.OWNER_CHOICES
        # Make assigned_to field optional
        self.fields['assigned_to'].required = False
        
        # Set choices for printer fields
        self.fields['printer_type'].choices = [('', '---------')] + list(ITAsset.PRINTER_TYPE_CHOICES)
        self.fields['connection_type'].choices = [('', '---------')] + list(ITAsset.CONNECTION_TYPE_CHOICES)
        
        # Update department choices for printer_department
        self.fields['printer_department'].queryset = Department.objects.all().order_by('name')
        self.fields['printer_department'].empty_label = "Select Department"
        self.fields['printer_department'].label_from_instance = lambda obj: obj.get_name_display()
        
        # Update employee choices for printer_responsible
        self.fields['printer_responsible'].queryset = Employee.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['printer_responsible'].empty_label = "Select Responsible Person"

    def clean_serial_number(self):
        serial_number = self.cleaned_data.get('serial_number')
        if serial_number:
            # Check if serial number is already in use by another asset
            if ITAsset.objects.filter(serial_number=serial_number).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError('This serial number is already in use.')
        return serial_number
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        assigned_to = cleaned_data.get('assigned_to')
        
        if status == 'ASSIGNED' and not assigned_to:
            raise forms.ValidationError("An assigned asset must have an assigned employee.")
        
        return cleaned_data 