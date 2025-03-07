/**
 * Weekly Export Sales Report JavaScript
 * Handles the report generation functionality for the Weekly Export Sales module.
 */

// Wait for document to be ready
document.addEventListener('DOMContentLoaded', function() {
    setupReportHandlers();
});

/**
 * Set up handlers for the report interface
 */
function setupReportHandlers() {
    // Report form submission
    $('#report-form').submit(function(e) {
        e.preventDefault();
        generateReport();
    });
    
    // Export to PDF button
    $('#export-pdf').click(function() {
        exportReportAsPdf();
    });
    
    // Export to Excel button
    $('#export-excel').click(function() {
        exportReportAsExcel();
    });
    
    // Print report button
    $('#print-report').click(function() {
        printReport();
    });
}

/**
 * Generate a report based on form inputs
 */
function generateReport() {
    const commodityCode = $('#report-commodity').val();
    const reportFormat = $('#report-format').val();
    const reportView = $('#report-view').val();
    
    if (!commodityCode) {
        alert('Please select a commodity');
        return;
    }
    
    // Show loading indicator
    showLoading('loading');
    
    // Make API request to generate report
    $.ajax({
        url: '/weekly_export_sales/generate_report',
        type: 'POST',
        data: {
            commodity_code: commodityCode,
            report_type: reportFormat,
            view_type: reportView
        },
        success: function(response) {
            hideLoading('loading');
            
            if (response.success) {
                // Update report display with the returned data
                displayReport(response.report);
                
                // Show export options
                $('.export-options').show();
            } else {
                // Show error message
                showError('report-container', 'Error generating report: ' + response.error);
            }
        },
        error: function() {
            hideLoading('loading');
            showError('report-container', 'Server error when generating report');
        }
    });
}

/**
 * Display the generated report
 * @param {Object} report - Report data
 */
function displayReport(report) {
    // Display commodity name and report date
    if (report.commodity_info) {
        $('#report-commodity-name').text(report.commodity_info.commodity_name);
    }
    
    if (report.report_date) {
        $('#report-week').text(formatDate(report.report_date));
    } else {
        // Use current date as fallback
        $('#report-week').text(formatDate(new Date()));
    }
    
    // Set generation date/time
    $('#generation-date').text(formatDate(new Date(), true));
    
    // Display placeholder or actual report
    if (!report.data_available) {
        // Show placeholder with message
        $('#report-placeholder .alert-secondary').html(`
            <p>${report.message || 'No data available for the selected report type.'}</p>
            <p>This section will provide structured, printer-friendly reports that follow the format of current PDF exports.</p>
        `);
    } else {
        // In a future implementation, this would handle the actual report data
        // For now, we're just showing the placeholder
    }
    
    // Show the report container
    $('#report-placeholder').show();
}

/**
 * Export the current report as PDF
 * Note: This is a placeholder function that would be implemented with a PDF library
 */
function exportReportAsPdf() {
    // This is a placeholder for PDF export functionality
    // In a real implementation, we would use a library like jsPDF or html2pdf
    alert('PDF export functionality will be implemented in a future update.');
}

/**
 * Export the current report as Excel
 * Note: This is a placeholder function that would be implemented with an Excel library
 */
function exportReportAsExcel() {
    // This is a placeholder for Excel export functionality
    // In a real implementation, we would use a library like SheetJS (xlsx)
    alert('Excel export functionality will be implemented in a future update.');
}

/**
 * Print the current report
 */
function printReport() {
    window.print();
}

/**
 * Format date string
 * @param {string|Date} dateInput - Date to format
 * @param {boolean} includeTime - Whether to include time in the output
 * @returns {string} Formatted date string
 */
function formatDate(dateInput, includeTime = false) {
    if (!dateInput) return 'N/A';
    
    const date = (dateInput instanceof Date) ? dateInput : new Date(dateInput);
    if (isNaN(date.getTime())) return 'Invalid Date';
    
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return date.toLocaleDateString('en-US', options);
}

/**
 * Format number with commas for thousands
 * @param {number} num - Number to format
 * @returns {string} Formatted number string
 */
function formatNumber(num) {
    if (isNaN(num)) return 'N/A';
    return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
}

/**
 * Format percentage change
 * @param {number} value - Percentage value to format
 * @returns {string} Formatted percentage string with sign
 */
function formatPercentChange(value) {
    if (isNaN(value)) return 'N/A';
    
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(1)}%`;
}