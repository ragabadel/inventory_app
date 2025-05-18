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