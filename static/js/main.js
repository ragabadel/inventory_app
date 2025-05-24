// Function to handle RTL support
function handleRTL() {
    const htmlElement = document.documentElement;
    const currentLang = htmlElement.lang;

    if (currentLang === 'ar') {
        htmlElement.dir = 'rtl';
        document.body.classList.add('rtl');
    } else {
        htmlElement.dir = 'ltr';
        document.body.classList.remove('rtl');
    }
}

// Function to handle form validation
function handleFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');

    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Function to handle Bootstrap tooltips
function handleTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Function to handle Bootstrap popovers
function handlePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Function to handle data tables
function handleDataTables() {
    const tables = document.querySelectorAll('.datatable');
    tables.forEach(table => {
        new DataTable(table, {
            language: {
                url: document.documentElement.lang === 'ar' ? 
                    '//cdn.datatables.net/plug-ins/1.10.24/i18n/Arabic.json' :
                    '//cdn.datatables.net/plug-ins/1.10.24/i18n/English.json'
            }
        });
    });
}

// Function to handle date pickers
function handleDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (input.value) {
            const date = new Date(input.value);
            input.value = date.toISOString().split('T')[0];
        }
    });
}

// Function to handle select2 dropdowns
function handleSelect2() {
    const selects = document.querySelectorAll('.select2');
    selects.forEach(select => {
        $(select).select2({
            theme: 'bootstrap-5',
            language: document.documentElement.lang
        });
    });
}

// Function to handle file inputs
function handleFileInputs() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            const label = this.nextElementSibling;
            if (label && fileName) {
                label.textContent = fileName;
            }
        });
    });
}

// Function to handle print functionality
function handlePrint() {
    const printButtons = document.querySelectorAll('.print-button');
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });
}

// Initialize all handlers when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    handleRTL();
    handleFormValidation();
    handleTooltips();
    handlePopovers();
    handleDataTables();
    handleDatePickers();
    handleSelect2();
    handleFileInputs();
    handlePrint();
}); 