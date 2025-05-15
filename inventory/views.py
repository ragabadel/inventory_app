# inventory/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Employee, ITAsset, Department, Position
from .forms import EmployeeForm, ITAssetForm
from django.http import HttpResponse
import openpyxl
from openpyxl import Workbook
from datetime import datetime

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
            Q(employee_id__icontains=search_query)
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
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'employees': page_obj,
        'departments': departments,
        'companies': Employee.COMPANY_CHOICES,
        'is_paginated': page_obj.has_other_pages(),
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
                        # Get or create department
                        department_name = row[5].value
                        department, _ = Department.objects.get_or_create(name=department_name)
                        
                        # Get or create position
                        position_name = row[6].value
                        position, _ = Position.objects.get_or_create(name=position_name)
                        
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