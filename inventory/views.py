# inventory/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Employee, ITAsset, Department, Position, AssetType, OwnerCompany, AssetHistory, Notification, WorkflowRequest, UserProfile
from .forms import EmployeeForm, ITAssetForm, WorkflowRequestForm, WorkflowRequestApprovalForm, UserProfileForm
from django.http import HttpResponse, JsonResponse
import openpyxl
from openpyxl import Workbook
from datetime import datetime, timedelta
from django.utils import timezone
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.conf import settings
import os
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from django.db.models.deletion import ProtectedError
from django.db import transaction

@login_required
def home(request):
    # Get total counts
    total_assets = ITAsset.objects.count()
    total_employees = Employee.objects.count()
    available_assets = ITAsset.objects.filter(status='available').count()
    assigned_assets = ITAsset.objects.filter(status='assigned').count()
    maintenance_assets = ITAsset.objects.filter(status='maintenance').count()
    retired_assets = ITAsset.objects.filter(status='retired').count()

    # Get asset type distribution
    asset_types = AssetType.objects.all()
    asset_type_distribution = []
    for asset_type in asset_types:
        count = ITAsset.objects.filter(asset_type=asset_type).count()
        asset_type_distribution.append({
            'name': asset_type.display_name,
            'count': count
        })

    # Get owner company distribution
    owner_companies = OwnerCompany.objects.all()
    owner_company_distribution = []
    for company in owner_companies:
        count = ITAsset.objects.filter(owner=company).count()
        owner_company_distribution.append({
            'name': company.name,
            'count': count
        })

    # Get recent assets
    recent_assets = ITAsset.objects.select_related('asset_type', 'owner', 'assigned_to').order_by('-id')[:5]

    # Get assets with expiring warranty (within 3 months)
    today = datetime.now().date()
    three_months_later = today + timedelta(days=90)
    expiring_warranty_assets = ITAsset.objects.filter(
        warranty_expiry__isnull=False,
        warranty_expiry__gte=today,
        warranty_expiry__lte=three_months_later
    ).select_related('asset_type', 'owner', 'assigned_to').order_by('warranty_expiry')

    # Get asset history
    asset_history = AssetHistory.objects.select_related(
        'asset', 'asset__asset_type', 'employee'
    ).order_by('-date')[:50]  # Show last 50 history entries

    context = {
        'total_assets': total_assets,
        'total_employees': total_employees,
        'available_assets': available_assets,
        'assigned_assets': assigned_assets,
        'maintenance_assets': maintenance_assets,
        'retired_assets': retired_assets,
        'asset_type_distribution': asset_type_distribution,
        'owner_company_distribution': owner_company_distribution,
        'recent_assets': recent_assets,
        'expiring_warranty_assets': expiring_warranty_assets,
        'asset_history': asset_history,
    }
    return render(request, 'inventory/home.html', context)

@login_required
def employee_list(request):
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    department_id = request.GET.get('department', '')
    company_id = request.GET.get('company', '')
    
    # Start with all employees
    employees = Employee.objects.all()
    
    # Apply search filter if provided
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(national_id__icontains=search_query)  # Add national_id to search
        )
    
    # Apply department filter if provided
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    # Apply company filter if provided
    if company_id:
        employees = employees.filter(company_id=company_id)
    
    # Get all departments for filter dropdown
    departments = Department.objects.all()
    
    # Get all companies for filter dropdown
    companies = OwnerCompany.objects.all()
    
    # Paginate the results
    paginator = Paginator(employees, 10)  # Show 10 employees per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get the current page number
    current_page = page_obj.number
    total_pages = paginator.num_pages
    
    # Calculate the range of page numbers to show
    if total_pages <= 5:
        page_range = range(1, total_pages + 1)
    else:
        if current_page <= 3:
            page_range = range(1, 6)
        elif current_page >= total_pages - 2:
            page_range = range(total_pages - 4, total_pages + 1)
        else:
            page_range = range(current_page - 2, current_page + 3)
    
    context = {
        'employees': page_obj,
        'departments': departments,
        'companies': companies,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'page_range': page_range,
        'current_page': current_page,
        'total_pages': total_pages,
    }
    
    return render(request, 'inventory/employee_list.html', context)

@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee "{employee.get_full_name()}" was successfully created.')
            return redirect('inventory:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm()
    
    return render(request, 'inventory/employee_form.html', {'form': form})

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'inventory/employee_detail.html', {'employee': employee})

@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee "{employee.get_full_name()}" was successfully updated.')
            return redirect('inventory:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'inventory/employee_form.html', {'form': form, 'employee': employee})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee_name = employee.get_full_name()
        employee.delete()
        messages.success(request, f'Employee "{employee_name}" was successfully deleted.')
        return redirect('inventory:employee_list')
    
    return render(request, 'inventory/employee_confirm_delete.html', {'employee': employee})

@login_required
def employee_toggle_status(request, pk):
    """Toggle employee's active status."""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee.is_active = not employee.is_active
        employee.save()
        
        status = 'activated' if employee.is_active else 'deactivated'
        messages.success(request, f'Employee "{employee.get_full_name()}" has been {status}.')
    
    return redirect('inventory:employee_detail', pk=employee.pk)

@login_required
def asset_assign(request):
    """View for assigning assets to employees."""
    if request.method == 'POST':
        asset_id = request.POST.get('asset')
        employee_id = request.POST.get('employee')
        
        try:
            asset = ITAsset.objects.get(pk=asset_id)
            employee = Employee.objects.get(pk=employee_id)
            
            # Create history record before updating asset
            AssetHistory.objects.create(
                asset=asset,
                action='assigned',
                employee=employee,
                notes=f'Asset assigned to {employee.get_full_name()}',
                created_by=request.user
            )
            
            asset.assigned_to = employee
            asset.status = 'assigned'
            asset.save()
            
            messages.success(request, f'Asset "{asset.name}" has been assigned to {employee.get_full_name()}.')
            return redirect('inventory:employee_detail', pk=employee.pk)
        except (ITAsset.DoesNotExist, Employee.DoesNotExist):
            messages.error(request, 'Invalid asset or employee selected.')
            return redirect('inventory:employee_list')
    
    # Get the employee from the query parameter
    employee_id = request.GET.get('employee')
    if employee_id:
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            messages.error(request, 'Employee not found.')
            return redirect('inventory:employee_list')
    else:
        employee = None
    
    # Get available assets
    available_assets = ITAsset.objects.filter(status='available')
    
    context = {
        'employee': employee,
        'available_assets': available_assets,
    }
    
    return render(request, 'inventory/asset_assign.html', context)

class NotificationMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Get unread notifications count
            context['unread_notifications_count'] = Notification.objects.filter(
                recipient=self.request.user,
                is_read=False
            ).count()
            
            # Get recent notifications
            context['notifications'] = Notification.objects.filter(
                recipient=self.request.user
            ).order_by('-created_at')[:5]  # Show last 5 notifications
            
            # Check for warranty expiry notifications
            today = timezone.now().date()
            expiring_warranty_assets = ITAsset.objects.filter(
                warranty_expiry__isnull=False,
                warranty_expiry__gte=today,
                warranty_expiry__lte=today + timedelta(days=30)  # Next 30 days
            )
            
            for asset in expiring_warranty_assets:
                if not Notification.objects.filter(
                    recipient=self.request.user,
                    notification_type='warranty_expiry',
                    asset=asset,
                    created_at__gte=today
                ).exists():
                    Notification.objects.create(
                        recipient=self.request.user,
                        notification_type='warranty_expiry',
                        title='Warranty Expiring Soon',
                        message=f'Warranty for {asset.name} will expire on {asset.warranty_expiry}',
                        asset=asset
                    )
        
        return context

class ITAssetListView(LoginRequiredMixin, NotificationMixin, ListView):
    model = ITAsset
    template_name = 'inventory/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get filter parameters
        search_query = self.request.GET.get('search', '')
        asset_type = self.request.GET.get('asset_type', '')
        status = self.request.GET.get('status', '')
        manufacturer = self.request.GET.get('manufacturer', '')
        
        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(serial_number__icontains=search_query) |
                Q(model__icontains=search_query) |
                Q(delivery_letter_code__icontains=search_query)
            )
        
        # Apply asset type filter
        if asset_type:
            queryset = queryset.filter(asset_type_id=asset_type)
        
        # Apply status filter
        if status:
            queryset = queryset.filter(status=status)
        
        # Apply manufacturer filter
        if manufacturer:
            queryset = queryset.filter(manufacturer__iexact=manufacturer)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asset_types'] = AssetType.objects.all()
        context['status_choices'] = ITAsset.STATUS_CHOICES
        
        # Get unique manufacturers, normalized to title case
        manufacturers = ITAsset.objects.exclude(manufacturer='').values_list('manufacturer', flat=True)
        normalized_manufacturers = set()
        for m in manufacturers:
            if m:
                normalized_manufacturers.add(m.strip().title())
        context['manufacturers'] = sorted(normalized_manufacturers)
        
        return context

class ITAssetDetailView(LoginRequiredMixin, DetailView):
    model = ITAsset
    template_name = 'inventory/asset_detail.html'
    context_object_name = 'asset'

class ITAssetCreateView(LoginRequiredMixin, CreateView):
    model = ITAsset
    form_class = ITAssetForm
    template_name = 'inventory/asset_form.html'
    success_url = reverse_lazy('inventory:asset_list')

    def form_valid(self, form):
        asset = form.save()
        # Create history record for new asset
        AssetHistory.objects.create(
            asset=asset,
            action='received',
            notes=f'Asset received and added to inventory',
            created_by=self.request.user
        )
        messages.success(self.request, 'IT Asset created successfully.')
        return super().form_valid(form)

class ITAssetUpdateView(LoginRequiredMixin, UpdateView):
    model = ITAsset
    form_class = ITAssetForm
    template_name = 'inventory/asset_form.html'
    success_url = reverse_lazy('inventory:asset_list')

    def form_valid(self, form):
        old_asset = self.get_object()
        old_status = old_asset.status
        old_assigned_to = old_asset.assigned_to
        
        asset = form.save()
        
        # Check if status changed
        if old_status != asset.status:
            action = asset.status
            notes = f'Asset status changed from {old_status} to {asset.status}'
            
            # If status changed to maintenance
            if asset.status == 'maintenance':
                notes = f'Asset sent for maintenance'
            
            # If status changed to retired
            elif asset.status == 'retired':
                notes = f'Asset retired from inventory'
            
            AssetHistory.objects.create(
                asset=asset,
                action=action,
                employee=asset.assigned_to,
                notes=notes,
                created_by=self.request.user
            )
        
        # Check if assigned employee changed
        if old_assigned_to != asset.assigned_to:
            if asset.assigned_to:
                # New assignment
                AssetHistory.objects.create(
                    asset=asset,
                    action='assigned',
                    employee=asset.assigned_to,
                    notes=f'Asset assigned to {asset.assigned_to.get_full_name()}',
                    created_by=self.request.user
                )
            else:
                # Returned to inventory
                AssetHistory.objects.create(
                    asset=asset,
                    action='returned',
                    employee=old_assigned_to,
                    notes=f'Asset returned from {old_assigned_to.get_full_name()}',
                    created_by=self.request.user
                )
        
        messages.success(self.request, 'IT Asset updated successfully.')
        return super().form_valid(form)

class ITAssetDeleteView(LoginRequiredMixin, DeleteView):
    model = ITAsset
    template_name = 'inventory/asset_confirm_delete.html'
    success_url = reverse_lazy('inventory:asset_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'IT Asset deleted successfully.')
        return super().delete(request, *args, **kwargs)

@login_required
def employee_upload(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if excel_file:
            try:
                wb = openpyxl.load_workbook(excel_file)
                ws = wb.active
                
                # Skip header row
                for row in ws.iter_rows(min_row=2):
                    try:
                        # Get or create department first
                        department_name = row[5].value
                        if department_name:
                            department, _ = Department.objects.get_or_create(name=department_name)
                            
                            # Get or create position with department
                            position_name = row[6].value
                            if position_name:
                                position, _ = Position.objects.get_or_create(
                                    name=position_name,
                                    department=department  # Set the department for the position
                                )
                            else:
                                position = None
                        else:
                            department = None
                            position = None
                        
                        # Get company
                        company_name = row[7].value
                        try:
                            company = OwnerCompany.objects.get(name=company_name)
                        except OwnerCompany.DoesNotExist:
                            messages.error(request, f'Row {row[0].row}: Company "{company_name}" not found. Please create it first.')
                            continue
                        
                        # Create employee
                        employee = Employee(
                            employee_id=row[0].value,
                            national_id=row[1].value,
                            first_name=row[2].value,
                            last_name=row[3].value,
                            email=row[4].value,
                            department=department,
                            position=position,
                            company=company,  # Use the company object
                            hire_date=row[8].value
                        )
                        employee.save()
                    except Exception as e:
                        messages.error(request, f'Error processing row: {str(e)}')
                        continue
                
                messages.success(request, 'Employees uploaded successfully!')
                return redirect('inventory:employee_list')
            except Exception as e:
                messages.error(request, f'Error uploading file: {str(e)}')
    
    return render(request, 'inventory/employee_upload.html')

@login_required
def download_employee_template(request):
    wb = Workbook()
    ws = wb.active
    
    # Add headers
    headers = [
        'Employee ID *',
        'National ID *',
        'First Name *',
        'Last Name *',
        'Email *',
        'Department *',
        'Position *',
        'Company *',
        'Hire Date *'
    ]
    ws.append(headers)
    
    # Add example row
    example = [
        'EMP001',
        '12345678901234',
        'John',
        'Doe',
        'john.doe@example.com',
        'IT',
        'Software Engineer',
        'CTP',
        '2024-01-01'
    ]
    ws.append(example)
    
    # Add available departments
    departments = Department.objects.all()
    if departments.exists():
        ws.append([])  # Add empty row
        ws.append(['Available Departments:'])
        for dept in departments:
            ws.append([dept.get_name_display()])
    
    # Add available companies
    companies = OwnerCompany.objects.all()
    if companies.exists():
        ws.append([])  # Add empty row
        ws.append(['Available Companies:'])
        for company in companies:
            ws.append([company.name])
    
    # Style the header row
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    
    # Style the sections headers
    if departments.exists():
        dept_header = ws.cell(row=4, column=1)
        dept_header.font = openpyxl.styles.Font(bold=True)
    
    if companies.exists():
        company_header = ws.cell(row=departments.count() + 6, column=1)
        company_header.font = openpyxl.styles.Font(bold=True)
    
    # Add data validation for company column
    company_validation = DataValidation(type="list", formula1=f'"{",".join(companies.values_list("name", flat=True))}"')
    company_validation.add(f'H2:H{len(example) + 1}')
    ws.add_data_validation(company_validation)
    
    # Add data validation for department column
    department_validation = DataValidation(type="list", formula1=f'"{",".join(departments.values_list("name", flat=True))}"')
    department_validation.add(f'F2:F{len(example) + 1}')
    ws.add_data_validation(department_validation)
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=employee_template.xlsx'
    
    wb.save(response)
    return response

@login_required
def download_employee_data(request):
    wb = Workbook()
    ws = wb.active
    
    # Add headers
    headers = [
        'Employee ID',
        'National ID',
        'First Name',
        'Last Name',
        'Email',
        'Department',
        'Position',
        'Company',
        'Hire Date'
    ]
    ws.append(headers)
    
    # Add employee data
    employees = Employee.objects.all()
    for employee in employees:
        row = [
            employee.employee_id,
            employee.national_id,
            employee.first_name,
            employee.last_name,
            employee.email,
            str(employee.department) if employee.department else '',
            str(employee.position) if employee.position else '',
            str(employee.company.name) if employee.company else '',  # Convert company to string
            employee.hire_date
        ]
        ws.append(row)
    
    # Style the header row
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=employees.xlsx'
    
    wb.save(response)
    return response

@login_required
def download_asset_template(request):
    wb = Workbook()
    ws = wb.active
    
    # Add headers
    headers = [
        'Asset Name *',
        'Asset Type *',
        'Serial Number *',
        'Model *',
        'Manufacturer',
        'Owner Company *',
        'Assigned Employee ID',
        'Wi-Fi MAC Address',
        'Ethernet MAC Address *',
        'Delivery Letter Code',
        'Purchase Date',
        'Receipt Date',
        'Warranty Expiry',
        'Status *'  # Added status field
    ]
    ws.append(headers)
    
    # Add example row
    example = [
        'Laptop-001',
        'laptop',  # Use the internal name, not display name
        'SN123456',
        'ThinkPad X1',
        'Lenovo',
        'CTP',  # Company name
        'EMP001',  # Employee ID
        '00:1A:2B:3C:4D:5E',
        '00:1A:2B:3C:4D:5F',
        'DL-2024-001',
        '2024-01-01',
        '2024-01-15',
        '2027-01-01',
        'available'  # Default status
    ]
    ws.append(example)
    
    # Add available asset types
    ws.append([])  # Add empty row
    ws.append(['Available Asset Types:'])
    ws.append(['Internal Name - Display Name'])
    for asset_type in AssetType.objects.all().order_by('name'):
        ws.append([f'{asset_type.name} - {asset_type.display_name}'])
    
    # Add available statuses
    ws.append([])  # Add empty row
    ws.append(['Available Statuses:'])
    ws.append(['Internal Name - Display Name'])
    for status_code, status_name in ITAsset.STATUS_CHOICES:
        ws.append([f'{status_code} - {status_name}'])
    
    # Add owner companies section
    ws.append([])  # Add empty row
    ws.append(['Owner Companies:'])
    for company in OwnerCompany.objects.all().order_by('name'):
        ws.append([company.name])
    
    # Add available employees section
    ws.append([])  # Add empty row
    ws.append(['Available Employees:'])
    ws.append(['Format: Employee ID - Full Name (Company)'])
    ws.append([])
    
    # Group employees by company
    for company in OwnerCompany.objects.all():
        ws.append([f'--- {company.name} Employees ---'])
        employees = Employee.objects.filter(
            is_active=True,
            company=company
        ).order_by('employee_id')
        
        for employee in employees:
            ws.append([f"{employee.employee_id} - {employee.get_full_name()} ({company.name})"])
        ws.append([])  # Add empty row between companies
    
    # Style the header row
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    
    # Style the sections headers
    ws.cell(row=4, column=1).font = openpyxl.styles.Font(bold=True)
    ws.cell(row=5, column=1).font = openpyxl.styles.Font(italic=True)  # Style the "Internal Name - Display Name" row
    
    # Find and style other section headers
    for row in range(1, ws.max_row + 1):
        cell = ws.cell(row=row, column=1)
        if cell.value in ['Owner Companies:', 'Available Employees:', 'Available Statuses:'] or \
           (cell.value and isinstance(cell.value, str) and cell.value.startswith('---')):
            cell.font = openpyxl.styles.Font(bold=True)
    
    # Add data validation for asset type column
    asset_types = AssetType.objects.all()
    if asset_types.exists():
        asset_type_validation = DataValidation(
            type="list",
            formula1=f'"{",".join(asset_types.values_list("name", flat=True))}"'
        )
        asset_type_validation.add(f'B2:B{len(example) + 1}')
        ws.add_data_validation(asset_type_validation)
    
    # Add data validation for company column
    companies = OwnerCompany.objects.all()
    if companies.exists():
        company_validation = DataValidation(
            type="list",
            formula1=f'"{",".join(companies.values_list("name", flat=True))}"'
        )
        company_validation.add(f'F2:F{len(example) + 1}')
        ws.add_data_validation(company_validation)
    
    # Add data validation for status column
    status_validation = DataValidation(
        type="list",
        formula1=f'"{",".join([status[0] for status in ITAsset.STATUS_CHOICES])}"'
    )
    status_validation.add(f'N2:N{len(example) + 1}')
    ws.add_data_validation(status_validation)
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=asset_template.xlsx'
    
    wb.save(response)
    return response

@login_required
def asset_upload(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if excel_file:
            try:
                wb = openpyxl.load_workbook(excel_file)
                ws = wb.active
                
                # Skip header row
                for row in ws.iter_rows(min_row=2):
                    try:
                        # Check required fields
                        required_fields = {
                            'name': row[0].value,
                            'asset_type': row[1].value,
                            'serial_number': row[2].value,
                            'model': row[3].value,
                            'owner_company': row[5].value,
                            'mac_address_ethernet': row[8].value,
                            'status': row[13].value  # Added status field
                        }
                        
                        # Validate required fields
                        missing_fields = [field for field, value in required_fields.items() if not value]
                        if missing_fields:
                            messages.error(request, f'Row {row[0].row}: Missing required fields: {", ".join(missing_fields)}')
                            continue

                        # Get or create asset type
                        asset_type_name = row[1].value
                        try:
                            asset_type = AssetType.objects.get(name__iexact=asset_type_name)
                        except AssetType.DoesNotExist:
                            messages.error(request, f'Row {row[0].row}: Asset Type "{asset_type_name}" not found. Please create it first.')
                            continue

                        # Get the owner company
                        owner_company_name = row[5].value
                        try:
                            owner_company = OwnerCompany.objects.get(name__iexact=owner_company_name)
                        except OwnerCompany.DoesNotExist:
                            messages.error(request, f'Row {row[0].row}: Owner Company "{owner_company_name}" not found. Please create it first.')
                            continue

                        # Validate status
                        status = row[13].value
                        if status not in dict(ITAsset.STATUS_CHOICES):
                            messages.error(request, f'Row {row[0].row}: Invalid status "{status}". Please use one of the available statuses.')
                            continue

                        # Get the assigned employee if provided
                        assigned_employee_id = row[6].value
                        assigned_employee = None
                        if assigned_employee_id:
                            try:
                                assigned_employee = Employee.objects.get(employee_id=assigned_employee_id)
                                # Verify employee belongs to the owner company
                                if assigned_employee.company != owner_company:
                                    messages.error(request, f'Row {row[0].row}: Employee {assigned_employee_id} does not belong to {owner_company_name}. Please assign an employee from the correct company.')
                                    continue
                            except Employee.DoesNotExist:
                                messages.error(request, f'Row {row[0].row}: Employee with ID {assigned_employee_id} not found. Please use a valid employee ID.')
                                continue
                        
                        # Create asset
                        asset = ITAsset(
                            name=row[0].value,
                            asset_type=asset_type,
                            serial_number=row[2].value,
                            model=row[3].value,
                            manufacturer=row[4].value,
                            owner=owner_company,
                            assigned_to=assigned_employee,
                            mac_address_wifi=row[7].value,
                            mac_address_ethernet=row[8].value,
                            delivery_letter_code=row[9].value,
                            status=status,
                            purchase_date=row[10].value,
                            receipt_date=row[11].value,
                            warranty_expiry=row[12].value
                        )
                        asset.save()

                        # Create history record for new asset
                        AssetHistory.objects.create(
                            asset=asset,
                            action='received',
                            employee=assigned_employee,
                            notes=f'Asset received and added to inventory via bulk upload',
                            created_by=request.user
                        )

                        # If asset is assigned, create assignment history
                        if assigned_employee:
                            AssetHistory.objects.create(
                                asset=asset,
                                action='assigned',
                                employee=assigned_employee,
                                notes=f'Asset assigned to {assigned_employee.get_full_name()} during bulk upload',
                                created_by=request.user
                            )

                        messages.success(request, f'Row {row[0].row}: Asset "{asset.name}" created successfully.')
                    except Exception as e:
                        messages.error(request, f'Row {row[0].row}: Error processing row: {str(e)}')
                        continue
                
                return redirect('inventory:asset_list')
            except Exception as e:
                messages.error(request, f'Error uploading file: {str(e)}')
    
    return render(request, 'inventory/asset_upload.html')

@login_required
def download_asset_data(request):
    wb = Workbook()
    ws = wb.active
    
    # Add headers
    headers = [
        'Asset Name',
        'Asset Type',
        'Serial Number',
        'Model',
        'Manufacturer',
        'Owner',
        'Wi-Fi MAC Address',
        'Ethernet MAC Address',
        'Delivery Letter Code',
        'Status',
        'Purchase Date',
        'Receipt Date',
        'Warranty Expiry'
    ]
    ws.append(headers)
    
    # Get filtered queryset using the same filters as the list view
    assets = ITAsset.objects.all()
    
    # Apply search filter
    search_query = request.GET.get('search', '')
    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(delivery_letter_code__icontains=search_query)
        )
    
    # Apply other filters
    asset_type = request.GET.get('asset_type', '')
    if asset_type:
        assets = assets.filter(asset_type_id=asset_type)
    
    status = request.GET.get('status', '')
    if status:
        assets = assets.filter(status=status)
    
    manufacturer = request.GET.get('manufacturer', '')
    if manufacturer:
        assets = assets.filter(manufacturer=manufacturer)
    
    # Add asset data
    for asset in assets:
        row = [
            asset.name,
            asset.asset_type.name,  # Use the internal name for consistency
            asset.serial_number,
            asset.model,
            asset.manufacturer,
            f"{asset.assigned_to.get_full_name()} ({asset.assigned_to.company})" if asset.assigned_to else '',
            asset.mac_address_wifi,
            asset.mac_address_ethernet,
            asset.delivery_letter_code,
            asset.status,  # Use the internal status value for consistency
            asset.purchase_date,
            asset.receipt_date,
            asset.warranty_expiry
        ]
        ws.append(row)
    
    # Style the header row
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=assets.xlsx'
    
    wb.save(response)
    return response

# Asset Type Views
class AssetTypeListView(LoginRequiredMixin, ListView):
    model = AssetType
    template_name = 'inventory/asset_type_list.html'
    context_object_name = 'asset_types'

class AssetTypeCreateView(LoginRequiredMixin, CreateView):
    model = AssetType
    template_name = 'inventory/asset_type_form.html'
    fields = ['name', 'display_name']
    success_url = reverse_lazy('inventory:asset_type_list')

    def form_valid(self, form):
        messages.success(self.request, 'Asset Type created successfully.')
        return super().form_valid(form)

class AssetTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = AssetType
    template_name = 'inventory/asset_type_form.html'
    fields = ['name', 'display_name']
    success_url = reverse_lazy('inventory:asset_type_list')

    def form_valid(self, form):
        messages.success(self.request, 'Asset Type updated successfully.')
        return super().form_valid(form)

class AssetTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = AssetType
    template_name = 'inventory/asset_type_confirm_delete.html'
    success_url = reverse_lazy('inventory:asset_type_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Asset Type deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Owner Company Views
class OwnerCompanyListView(LoginRequiredMixin, ListView):
    model = OwnerCompany
    template_name = 'inventory/owner_company_list.html'
    context_object_name = 'companies'

class OwnerCompanyCreateView(LoginRequiredMixin, CreateView):
    model = OwnerCompany
    template_name = 'inventory/owner_company_form.html'
    fields = ['code', 'name']
    success_url = reverse_lazy('inventory:owner_company_list')

    def form_valid(self, form):
        messages.success(self.request, 'Owner Company created successfully.')
        return super().form_valid(form)

class OwnerCompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = OwnerCompany
    template_name = 'inventory/owner_company_form.html'
    fields = ['code', 'name']
    success_url = reverse_lazy('inventory:owner_company_list')

    def form_valid(self, form):
        messages.success(self.request, 'Owner Company updated successfully.')
        return super().form_valid(form)

class OwnerCompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = OwnerCompany
    template_name = 'inventory/owner_company_confirm_delete.html'
    success_url = reverse_lazy('inventory:owner_company_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Owner Company deleted successfully.')
        return super().delete(request, *args, **kwargs)

class EmployeePDFView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'inventory/employee_pdf.html'
    
    def get(self, request, *args, **kwargs):
        employee = self.get_object()
        html_string = render_to_string(self.template_name, {'employee': employee})
        
        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="employee_{employee.employee_id}.pdf"'
        
        # Generate PDF
        pisa_status = pisa.CreatePDF(
            html_string,
            dest=response,
            encoding='utf-8'
        )
        
        if pisa_status.err:
            return HttpResponse('Error generating PDF')
        
        return response

class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'inventory/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get search and filter parameters
        search_query = self.request.GET.get('search', '')
        department_id = self.request.GET.get('department', '')
        company_id = self.request.GET.get('company', '')
        
        # Apply search filter if provided
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(employee_id__icontains=search_query) |
                Q(national_id__icontains=search_query)
            )
        
        # Apply department filter if provided
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # Apply company filter if provided
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['companies'] = OwnerCompany.objects.all()
        
        # Add pagination context
        paginator = context['paginator']
        page_obj = context['page_obj']
        
        # Get the current page number
        current_page = page_obj.number
        total_pages = paginator.num_pages
        
        # Calculate the range of page numbers to show
        if total_pages <= 5:
            page_range = range(1, total_pages + 1)
        else:
            if current_page <= 3:
                page_range = range(1, 6)
            elif current_page >= total_pages - 2:
                page_range = range(total_pages - 4, total_pages + 1)
            else:
                page_range = range(current_page - 2, current_page + 3)
        
        context.update({
            'is_paginated': page_obj.has_other_pages(),
            'page_obj': page_obj,
            'page_range': page_range,
            'current_page': current_page,
            'total_pages': total_pages,
        })
        
        return context

class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'inventory/employee_detail.html'
    context_object_name = 'employee'

class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'inventory/employee_form.html'
    success_url = reverse_lazy('inventory:employee_list')

    def form_valid(self, form):
        messages.success(self.request, 'Employee created successfully.')
        return super().form_valid(form)

class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'inventory/employee_form.html'
    success_url = reverse_lazy('inventory:employee_list')

    def form_valid(self, form):
        messages.success(self.request, 'Employee updated successfully.')
        return super().form_valid(form)

class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'inventory/employee_confirm_delete.html'
    success_url = reverse_lazy('inventory:employee_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Employee deleted successfully.')
        return super().delete(request, *args, **kwargs)

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'inventory/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = self.get_queryset().filter(is_read=False).count()
        return context

class NotificationMarkAsReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})

class WorkflowRequestCreateView(LoginRequiredMixin, CreateView):
    model = WorkflowRequest
    form_class = WorkflowRequestForm
    template_name = 'inventory/workflow_request_form.html'
    success_url = reverse_lazy('inventory:workflow_request_list')

    def form_valid(self, form):
        form.instance.requester = self.request.user
        response = super().form_valid(form)
        
        # Create notification for IT department manager
        it_manager = User.objects.filter(groups__name='IT_Manager').first()
        if it_manager:
            Notification.objects.create(
                notification_type='new_device_request',
                title=f'New {form.instance.get_request_type_display()}',
                message=f'{self.request.user.get_full_name()} has submitted a new request: {form.instance.description}',
                recipient=it_manager,
                asset=form.instance.asset
            )
        
        messages.success(self.request, 'Request submitted successfully.')
        return response

class WorkflowRequestListView(LoginRequiredMixin, ListView):
    model = WorkflowRequest
    template_name = 'inventory/workflow_request_list.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.groups.filter(name='IT_Manager').exists():
            return WorkflowRequest.objects.all()
        return WorkflowRequest.objects.filter(requester=self.request.user)

class WorkflowRequestDetailView(LoginRequiredMixin, DetailView):
    model = WorkflowRequest
    template_name = 'inventory/workflow_request_detail.html'
    context_object_name = 'request'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.groups.filter(name='IT_Manager').exists():
            context['approval_form'] = WorkflowRequestApprovalForm(instance=self.object)
        return context

class WorkflowRequestApproveView(LoginRequiredMixin, UpdateView):
    model = WorkflowRequest
    form_class = WorkflowRequestApprovalForm
    template_name = 'inventory/workflow_request_approve.html'

    def get_queryset(self):
        return WorkflowRequest.objects.filter(status='pending')

    def form_valid(self, form):
        if not self.request.user.groups.filter(name='IT_Manager').exists():
            messages.error(self.request, 'You do not have permission to approve requests.')
            return redirect('inventory:workflow_request_list')

        form.instance.approved_by = self.request.user
        form.instance.approval_date = timezone.now()
        response = super().form_valid(form)

        # Create notification for requester
        Notification.objects.create(
            notification_type='request_approved' if form.instance.status == 'approved' else 'request_rejected',
            title=f'Request {form.instance.get_status_display()}',
            message=f'Your request has been {form.instance.get_status_display().lower()}.',
            recipient=form.instance.requester,
            asset=form.instance.asset
        )

        messages.success(self.request, f'Request {form.instance.get_status_display().lower()}.')
        return response

    def get_success_url(self):
        return reverse_lazy('inventory:workflow_request_detail', kwargs={'pk': self.object.pk})

@login_required
def update_language(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Language preference updated successfully.'))
            return redirect('inventory:landing')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    
    return render(request, 'inventory/language_form.html', {'form': form})

@login_required
def create_device_request(request):
    """Create a new device request."""
    if request.method == 'POST':
        form = WorkflowRequestForm(request.POST)
        if form.is_valid():
            workflow_request = form.save(commit=False)
            workflow_request.requester = request.user
            workflow_request.request_type = 'new_device'
            workflow_request.save()
            
            # Create notification for IT manager
            it_manager = User.objects.filter(groups__name='IT_Manager').first()
            if it_manager:
                Notification.objects.create(
                    notification_type='new_device_request',
                    title='New Device Request',
                    message=f'{request.user.get_full_name()} has requested a new device: {workflow_request.description}',
                    recipient=it_manager
                )
            
            messages.success(request, 'Device request submitted successfully.')
            return redirect('inventory:workflow_request_detail', pk=workflow_request.pk)
    else:
        form = WorkflowRequestForm()
    
    return render(request, 'inventory/workflow_request_form.html', {
        'form': form,
        'title': 'Request New Device'
    })

@login_required
def create_maintenance_request(request, asset_id):
    """Create a maintenance request for a specific asset."""
    asset = get_object_or_404(ITAsset, pk=asset_id)
    
    if request.method == 'POST':
        form = WorkflowRequestForm(request.POST)
        if form.is_valid():
            workflow_request = form.save(commit=False)
            workflow_request.requester = request.user
            workflow_request.request_type = 'maintenance'
            workflow_request.asset = asset
            workflow_request.save()
            
            # Create notification for IT manager
            it_manager = User.objects.filter(groups__name='IT_Manager').first()
            if it_manager:
                Notification.objects.create(
                    notification_type='maintenance_request',
                    title='Maintenance Request',
                    message=f'{request.user.get_full_name()} has requested maintenance for {asset.name}: {workflow_request.description}',
                    recipient=it_manager,
                    asset=asset
                )
            
            messages.success(request, 'Maintenance request submitted successfully.')
            return redirect('inventory:workflow_request_detail', pk=workflow_request.pk)
    else:
        form = WorkflowRequestForm()
    
    return render(request, 'inventory/workflow_request_form.html', {
        'form': form,
        'title': f'Request Maintenance for {asset.name}',
        'asset': asset
    })

@login_required
def report_damaged_device(request, asset_id):
    """Report a damaged device."""
    asset = get_object_or_404(ITAsset, pk=asset_id)
    
    if request.method == 'POST':
        form = WorkflowRequestForm(request.POST)
        if form.is_valid():
            workflow_request = form.save(commit=False)
            workflow_request.requester = request.user
            workflow_request.request_type = 'damage_report'
            workflow_request.asset = asset
            workflow_request.save()
            
            # Create notification for IT manager
            it_manager = User.objects.filter(groups__name='IT_Manager').first()
            if it_manager:
                Notification.objects.create(
                    notification_type='damaged_device',
                    title='Damaged Device Report',
                    message=f'{request.user.get_full_name()} has reported damage to {asset.name}: {workflow_request.description}',
                    recipient=it_manager,
                    asset=asset
                )
            
            messages.success(request, 'Damage report submitted successfully.')
            return redirect('inventory:workflow_request_detail', pk=workflow_request.pk)
    else:
        form = WorkflowRequestForm()
    
    return render(request, 'inventory/workflow_request_form.html', {
        'form': form,
        'title': f'Report Damage for {asset.name}',
        'asset': asset
    })

@login_required
def report_lost_device(request, asset_id):
    """Report a lost device."""
    asset = get_object_or_404(ITAsset, pk=asset_id)
    
    if request.method == 'POST':
        form = WorkflowRequestForm(request.POST)
        if form.is_valid():
            workflow_request = form.save(commit=False)
            workflow_request.requester = request.user
            workflow_request.request_type = 'loss_report'
            workflow_request.asset = asset
            workflow_request.save()
            
            # Create notification for IT manager
            it_manager = User.objects.filter(groups__name='IT_Manager').first()
            if it_manager:
                Notification.objects.create(
                    notification_type='lost_device',
                    title='Lost Device Report',
                    message=f'{request.user.get_full_name()} has reported {asset.name} as lost: {workflow_request.description}',
                    recipient=it_manager,
                    asset=asset
                )
            
            messages.success(request, 'Loss report submitted successfully.')
            return redirect('inventory:workflow_request_detail', pk=workflow_request.pk)
    else:
        form = WorkflowRequestForm()
    
    return render(request, 'inventory/workflow_request_form.html', {
        'form': form,
        'title': f'Report Loss of {asset.name}',
        'asset': asset
    })

class UserManagementView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'inventory/user_management.html'
    context_object_name = 'users'
    paginate_by = 12

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='IT_Manager').exists()

    def get_queryset(self):
        queryset = User.objects.all()
        
        # Search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Filter by group
        group_id = self.request.GET.get('group')
        if group_id:
            queryset = queryset.filter(groups__id=group_id)
        
        # Filter by status
        is_active = self.request.GET.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == '1')
        
        return queryset.select_related('profile').prefetch_related('groups')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        return context

class CreateUserView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'inventory/user_form.html'
    success_url = reverse_lazy('inventory:user_management')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='IT_Manager').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        context['permissions'] = Permission.objects.all().order_by('content_type__app_label', 'name')
        context['title'] = _('Create New User')
        return context

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            
            # Create user profile
            UserProfile.objects.create(
                user=self.object,
                language_preference='en'  # Default language
            )
            
            # Add user to selected groups
            group_ids = self.request.POST.getlist('groups')
            if group_ids:
                self.object.groups.set(group_ids)
                
                # Set permissions based on groups
                for group in self.object.groups.all():
                    # Add group permissions to user
                    self.object.user_permissions.add(*group.permissions.all())
            
            # Add individual permissions if specified
            permission_ids = self.request.POST.getlist('permissions')
            if permission_ids:
                from django.contrib.auth.models import Permission
                permissions = Permission.objects.filter(id__in=permission_ids)
                self.object.user_permissions.add(*permissions)
            
            messages.success(self.request, _('User created successfully with appropriate permissions.'))
            return response

class EditUserView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'inventory/user_form.html'
    fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
    success_url = reverse_lazy('inventory:user_management')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='IT_Manager').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        context['permissions'] = Permission.objects.all().order_by('content_type__app_label', 'name')
        context['title'] = _('Edit User')
        return context

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            
            # Update user groups
            group_ids = self.request.POST.getlist('groups')
            self.object.groups.set(group_ids)
            
            # Update individual permissions
            permission_ids = self.request.POST.getlist('permissions')
            self.object.user_permissions.clear()  # Clear existing permissions
            if permission_ids:
                from django.contrib.auth.models import Permission
                permissions = Permission.objects.filter(id__in=permission_ids)
                self.object.user_permissions.add(*permissions)
            
            # Add group permissions
            for group in self.object.groups.all():
                self.object.user_permissions.add(*group.permissions.all())
            
            messages.success(self.request, _('User updated successfully with appropriate permissions.'))
            return response

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='IT_Manager').exists())
def activate_user(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        user.is_active = True
        user.save()
        messages.success(request, _('User activated successfully.'))
    return redirect('inventory:user_management')

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='IT_Manager').exists())
def deactivate_user(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        user.is_active = False
        user.save()
        messages.success(request, _('User deactivated successfully.'))
    return redirect('inventory:user_management')

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='IT_Manager').exists())
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, _('User "%s" deleted successfully.') % username)
        return redirect('inventory:user_management')
    return render(request, 'inventory/user_confirm_delete.html', {'user': user})

class AssetHistoryView(LoginRequiredMixin, ListView):
    model = AssetHistory
    template_name = 'inventory/asset_history.html'
    context_object_name = 'history_entries'
    paginate_by = 20

    def get_queryset(self):
        queryset = AssetHistory.objects.select_related(
            'asset', 'asset__asset_type', 'employee', 'created_by'
        ).order_by('-date')
        
        # Filter by asset if specified
        asset_id = self.request.GET.get('asset')
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
        
        # Filter by action type if specified
        action = self.request.GET.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by date range if specified
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assets'] = ITAsset.objects.all()
        context['action_choices'] = AssetHistory.ACTION_CHOICES
        return context

# Department Views
class DepartmentListView(LoginRequiredMixin, NotificationMixin, ListView):
    model = Department
    template_name = 'inventory/department_list.html'
    context_object_name = 'departments'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

class DepartmentCreateView(LoginRequiredMixin, NotificationMixin, CreateView):
    model = Department
    template_name = 'inventory/department_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('inventory:department_list')

    def form_valid(self, form):
        messages.success(self.request, _('Department created successfully.'))
        return super().form_valid(form)

class DepartmentUpdateView(LoginRequiredMixin, NotificationMixin, UpdateView):
    model = Department
    template_name = 'inventory/department_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('inventory:department_list')

    def form_valid(self, form):
        messages.success(self.request, _('Department updated successfully.'))
        return super().form_valid(form)

class DepartmentDeleteView(LoginRequiredMixin, NotificationMixin, DeleteView):
    model = Department
    template_name = 'inventory/department_confirm_delete.html'
    success_url = reverse_lazy('inventory:department_list')

    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, _('Department deleted successfully.'))
            return response
        except ProtectedError:
            messages.error(request, _('Cannot delete this department because it is associated with employees.'))
            return redirect('inventory:department_list')

class LandingPageView(TemplateView):
    template_name = 'inventory/landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('IT Solutions Management - Professional IT Services')
        return context  