// Chart.js Defaults
Chart.defaults.font.family = "'Inter', system-ui, -apple-system, sans-serif";
Chart.defaults.color = '#6B7280';
Chart.defaults.plugins.tooltip.backgroundColor = '#1F2937';
Chart.defaults.plugins.tooltip.titleColor = '#F9FAFB';
Chart.defaults.plugins.tooltip.bodyColor = '#F9FAFB';
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 8;

// Chart.js Theme Colors
const chartColors = {
    primary: {
        default: '#0EA5E9',
        light: '#BAE6FD',
        dark: '#0369A1'
    },
    success: {
        default: '#22C55E',
        light: '#DCFCE7',
        dark: '#16A34A'
    },
    warning: {
        default: '#F59E0B',
        light: '#FEF3C7',
        dark: '#D97706'
    },
    danger: {
        default: '#EF4444',
        light: '#FEE2E2',
        dark: '#DC2626'
    },
    gray: {
        default: '#6B7280',
        light: '#F3F4F6',
        dark: '#374151'
    }
};

// Chart.js Helpers
const createChart = (ctx, config) => {
    return new Chart(ctx, {
        ...config,
        options: {
            ...config.options,
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                ...config.options?.plugins,
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
};

// Form Validation
const validateForm = (form) => {
    const inputs = form.querySelectorAll('input, select, textarea');
    let isValid = true;

    inputs.forEach(input => {
        if (input.hasAttribute('required') && !input.value) {
            isValid = false;
            input.classList.add('border-danger-500');
            
            // Add error message
            const errorMessage = document.createElement('p');
            errorMessage.className = 'mt-1 text-sm text-danger-600';
            errorMessage.textContent = 'This field is required';
            
            const existingError = input.parentNode.querySelector('.text-danger-600');
            if (!existingError) {
                input.parentNode.appendChild(errorMessage);
            }
        } else {
            input.classList.remove('border-danger-500');
            const existingError = input.parentNode.querySelector('.text-danger-600');
            if (existingError) {
                existingError.remove();
            }
        }
    });

    return isValid;
};

// File Upload Preview
const handleFileUpload = (input, previewContainer) => {
    const files = input.files;
    
    if (!files.length) return;
    
    previewContainer.innerHTML = '';
    
    Array.from(files).forEach(file => {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const preview = document.createElement('div');
            preview.className = 'relative group';
            
            if (file.type.startsWith('image/')) {
                preview.innerHTML = `
                    <img src="${e.target.result}" alt="${file.name}" class="h-20 w-20 object-cover rounded-lg">
                    <button type="button" class="absolute hidden group-hover:flex items-center justify-center inset-0 bg-gray-900 bg-opacity-50 rounded-lg">
                        <i class="fas fa-times text-white"></i>
                    </button>
                `;
            } else {
                preview.innerHTML = `
                    <div class="h-20 w-20 flex items-center justify-center bg-gray-100 rounded-lg">
                        <i class="fas fa-file text-gray-400 text-xl"></i>
                    </div>
                    <button type="button" class="absolute hidden group-hover:flex items-center justify-center inset-0 bg-gray-900 bg-opacity-50 rounded-lg">
                        <i class="fas fa-times text-white"></i>
                    </button>
                `;
            }
            
            preview.querySelector('button').addEventListener('click', () => {
                preview.remove();
                // Clear the file input if it's the last preview
                if (!previewContainer.children.length) {
                    input.value = '';
                }
            });
            
            previewContainer.appendChild(preview);
        };
        
        reader.readAsDataURL(file);
    });
};

// Data Export
const exportToExcel = (tableId, filename) => {
    const table = document.getElementById(tableId);
    const wb = XLSX.utils.table_to_book(table);
    XLSX.writeFile(wb, `${filename}.xlsx`);
};

const exportToPDF = (tableId, filename) => {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    doc.autoTable({
        html: `#${tableId}`,
        theme: 'grid',
        styles: {
            font: 'Inter',
            fontSize: 10,
            cellPadding: 5
        },
        headStyles: {
            fillColor: [31, 41, 55],
            textColor: [255, 255, 255],
            fontSize: 11,
            fontStyle: 'bold'
        },
        alternateRowStyles: {
            fillColor: [249, 250, 251]
        }
    });
    
    doc.save(`${filename}.pdf`);
};

// Notifications
const markNotificationAsRead = async (notificationId) => {
    try {
        const response = await fetch(`/notifications/${notificationId}/mark-as-read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            const notification = document.querySelector(`[data-notification-id="${notificationId}"]`);
            notification.classList.remove('bg-primary-50');
            notification.classList.add('bg-gray-50');
            
            // Update badge count
            const badge = document.getElementById('notificationBadge');
            const count = parseInt(badge.textContent) - 1;
            if (count > 0) {
                badge.textContent = count;
            } else {
                badge.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
};

// Dark Mode Toggle
const toggleDarkMode = () => {
    const html = document.documentElement;
    const isDark = html.classList.contains('dark');
    
    if (isDark) {
        html.classList.remove('dark');
        localStorage.setItem('darkMode', 'light');
    } else {
        html.classList.add('dark');
        localStorage.setItem('darkMode', 'dark');
    }
};

// Initialize Dark Mode
const initDarkMode = () => {
    const darkMode = localStorage.getItem('darkMode');
    if (darkMode === 'dark' || (!darkMode && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
    }
};

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    
    // Initialize htmx
    htmx.config.useTemplateFragments = true;
    
    // Initialize tooltips
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        tippy(element, {
            content: element.getAttribute('data-tooltip'),
            placement: element.getAttribute('data-tooltip-placement') || 'top'
        });
    });
    
    // Initialize file uploads
    document.querySelectorAll('[data-file-upload]').forEach(input => {
        const previewContainer = document.querySelector(input.getAttribute('data-preview'));
        if (previewContainer) {
            input.addEventListener('change', () => handleFileUpload(input, previewContainer));
        }
    });
    
    // Initialize form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });
}); 