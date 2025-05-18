# inventory/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Employee, ITAsset, Department, Position, AssetType, OwnerCompany
from .forms import EmployeeForm, ITAssetForm
from django.http import HttpResponse
import openpyxl
from openpyxl import Workbook
from datetime import datetime

@login_required
def home(request):
    return render(request, 'inventory/home.html')

@login_required
def employee_list(request):
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    department_id = request.GET.get('department', '')
    company = request.GET.get('company', '')
    
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
    if company:
        employees = employees.filter(company=company)
    
    # Get all departments for filter dropdown
    departments = Department.objects.all()
    
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
        'companies': Employee.COMPANY_CHOICES,
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

class ITAssetListView(LoginRequiredMixin, ListView):
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
            queryset = queryset.filter(manufacturer=manufacturer)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asset_types'] = AssetType.objects.all()
        context['status_choices'] = ITAsset.STATUS_CHOICES
        context['manufacturers'] = ITAsset.objects.exclude(manufacturer='').values_list('manufacturer', flat=True).distinct()
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
        messages.success(self.request, 'IT Asset created successfully.')
        return super().form_valid(form)

class ITAssetUpdateView(LoginRequiredMixin, UpdateView):
    model = ITAsset
    form_class = ITAssetForm
    template_name = 'inventory/asset_form.html'
    success_url = reverse_lazy('inventory:asset_list')

    def form_valid(self, form):
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
                        
                        # Create employee
                        employee = Employee(
                            employee_id=row[0].value,
                            national_id=row[1].value,
                            first_name=row[2].value,
                            last_name=row[3].value,
                            email=row[4].value,
                            department=department,
                            position=position,
                            company=row[7].value,
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
        'Main Company',
        '2024-01-01'
    ]
    ws.append(example)
    
    # Add available departments
    departments = Department.objects.all()
    if departments.exists():
        ws.append([])  # Add empty row
        ws.append(['Available Departments:'])
        for dept in departments:
            ws.append([dept.name])
    
    # Style the header row
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    
    # Style the departments section
    if departments.exists():
        dept_header = ws.cell(row=4, column=1)
        dept_header.font = openpyxl.styles.Font(bold=True)
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = openpyxl.utils.get_column_letter(column[0].column)
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
            employee.company,
            employee.hire_date
        ]
        ws.append(row)
    
    # Style the header row
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = openpyxl.utils.get_column_letter(column[0].column)
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
        'Model',
        'Manufacturer',
        'Owner',
        'Wi-Fi MAC Address',
        'Ethernet MAC Address',
        'Delivery Letter Code',
        'Status *',
        'Purchase Date',
        'Receipt Date',
        'Warranty Expiry'
    ]
    ws.append(headers)
    
    # Add example row
    example = [
        'Laptop-001',
        'laptop',  # Use the internal name, not display name
        'SN123456',
        'ThinkPad X1',
        'Lenovo',
        'John Doe (CTP)',
        '00:1A:2B:3C:4D:5E',
        '00:1A:2B:3C:4D:5F',
        'DL-2024-001',
        'available',  # Use the internal status value
        '2024-01-01',
        '2024-01-15',
        '2027-01-01'
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
    for status in ITAsset.STATUS_CHOICES:
        ws.append([status[0]])  # Use the internal status value
    
    # Add owner companies section
    ws.append([])  # Add empty row
    ws.append(['Owner Companies:'])
    for company in OwnerCompany.objects.all().order_by('name'):
        ws.append([company.name])
    
    # Add available owners (employees) with their companies
    ws.append([])  # Add empty row
    ws.append(['Available Owners (Employees):'])
    ws.append(['Format: Full Name (Company)'])
    ws.append([])  # Add empty row
    
    # Group employees by company
    for company in OwnerCompany.objects.all():
        ws.append([f'--- {company.name} Employees ---'])
        employees = Employee.objects.filter(
            is_active=True,
            company=company.code
        ).order_by('first_name', 'last_name')
        
        for employee in employees:
            ws.append([f"{employee.first_name} {employee.last_name} ({company.name})"])
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
        if cell.value in ['Available Statuses:', 'Owner Companies:', 'Available Owners (Employees):'] or \
           (cell.value and isinstance(cell.value, str) and cell.value.startswith('---')):
            cell.font = openpyxl.styles.Font(bold=True)
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = openpyxl.utils.get_column_letter(column[0].column)
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
                        # Get or create asset type
                        asset_type_name = row[1].value
                        if asset_type_name:
                            try:
                                asset_type = AssetType.objects.get(name__iexact=asset_type_name)
                            except AssetType.DoesNotExist:
                                messages.warning(request, f'Asset Type "{asset_type_name}" not found. Please create it first.')
                                continue

                        # Get the owner if provided
                        owner_name = row[5].value
                        owner = None
                        if owner_name:
                            try:
                                # Try to find owner by full name
                                first_name, last_name = owner_name.split(' ', 1)
                                owner = Employee.objects.get(first_name=first_name, last_name=last_name)
                            except (ValueError, Employee.DoesNotExist):
                                messages.warning(request, f'Owner "{owner_name}" not found. Asset will be created without owner.')
                        
                        # Create asset
                        asset = ITAsset(
                            name=row[0].value,
                            asset_type=asset_type,
                            serial_number=row[2].value,
                            model=row[3].value,
                            manufacturer=row[4].value,
                            assigned_to=owner,
                            mac_address_wifi=row[6].value,
                            mac_address_ethernet=row[7].value,
                            delivery_letter_code=row[8].value,
                            status=row[9].value,
                            purchase_date=row[10].value,
                            receipt_date=row[11].value,
                            warranty_expiry=row[12].value
                        )
                        asset.save()
                    except Exception as e:
                        messages.error(request, f'Error processing row: {str(e)}')
                        continue
                
                messages.success(request, 'Assets uploaded successfully!')
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
        column_letter = openpyxl.utils.get_column_letter(column[0].column)
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