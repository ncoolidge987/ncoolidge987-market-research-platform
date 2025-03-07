/**
 * Weekly Export Sales Visualization JavaScript
 * Handles the interactive visualization functionality for the Weekly Export Sales module.
 */

// Wait for document to be ready
document.addEventListener('DOMContentLoaded', function() {
    setupFormHandlers();
});

/**
 * Set up form handlers for the visualization interface
 */
function setupFormHandlers() {
    // When commodity is selected, load years
    $('#commodity').change(function() {
        const commodityCode = $(this).val();
        if (commodityCode) {
            fetchMarketingYears(commodityCode);
        } else {
            resetYearDropdowns();
            disableControls();
        }
    });

    // Update countries button
    $('#update-countries').click(function() {
        const commodityCode = $('#commodity').val();
        const startYear = $('#start-year').val();
        const endYear = $('#end-year').val();

        if (commodityCode && startYear && endYear) {
            fetchCountries(commodityCode, startYear, endYear);
        } else {
            alert('Please select a commodity and year range first');
        }
    });

    // Form submission
    $('#visualization-form').submit(function(e) {
        e.preventDefault();
        generateVisualization();
    });

    // Enable Update Plot button when years are selected
    $('#start-year, #end-year').change(function() {
        if ($('#commodity').val() && $('#start-year').val() && $('#end-year').val()) {
            $('#update-plot').prop('disabled', false);
            $('#update-countries').prop('disabled', false);
            $('#countries').prop('disabled', false);
        } else {
            $('#update-plot').prop('disabled', true);
        }
    });
}

/**
 * Fetch marketing years for the selected commodity
 * @param {string} commodityCode - Selected commodity code
 */
function fetchMarketingYears(commodityCode) {
    showLoading('loading');
    
    $.ajax({
        url: '/weekly_export_sales/get_years',
        type: 'POST',
        data: {
            commodity_code: commodityCode
        },
        success: function(response) {
            hideLoading('loading');

            if (response.success) {
                const years = response.years;

                // Populate start year dropdown
                let startYearOptions = '<option value="">Start Year</option>';
                years.forEach(year => {
                    startYearOptions += `<option value="${year}">${year-1}/${year}</option>`;
                });
                $('#start-year').html(startYearOptions).prop('disabled', false);

                // Populate end year dropdown
                let endYearOptions = '<option value="">End Year</option>';
                years.forEach(year => {
                    endYearOptions += `<option value="${year}">${year-1}/${year}</option>`;
                });
                $('#end-year').html(endYearOptions).prop('disabled', false);

                // Set defaults to last 5 years
                if (years.length > 0) {
                    const defaultStartIndex = Math.max(0, years.length - 5);
                    $('#start-year').val(years[defaultStartIndex]);
                    $('#end-year').val(years[years.length - 1]);

                    // Enable update countries button
                    $('#update-countries').prop('disabled', false);
                    $('#update-plot').prop('disabled', false);
                }
            } else {
                alert('Error loading years: ' + response.error);
                resetYearDropdowns();
            }
        },
        error: function() {
            hideLoading('loading');
            alert('Server error when loading years');
            resetYearDropdowns();
        }
    });
}

/**
 * Fetch countries for the selected commodity and years
 * @param {string} commodityCode - Selected commodity code
 * @param {string} startYear - Start marketing year
 * @param {string} endYear - End marketing year
 */
function fetchCountries(commodityCode, startYear, endYear) {
    showLoading('loading');

    $.ajax({
        url: '/weekly_export_sales/get_countries',
        type: 'POST',
        data: {
            commodity_code: commodityCode,
            start_year: startYear,
            end_year: endYear
        },
        success: function(response) {
            hideLoading('loading');

            if (response.success) {
                const countries = response.countries;

                // Populate countries dropdown
                let countryOptions = '<option value="All Countries">All Countries</option>';
                countries.forEach(country => {
                    countryOptions += `<option value="${country}">${country}</option>`;
                });

                $('#countries').html(countryOptions).prop('disabled', false);
                $('#countries').val('All Countries'); // Default to All Countries
                $('#update-plot').prop('disabled', false);
            } else {
                alert('Error loading countries: ' + response.error);
            }
        },
        error: function() {
            hideLoading('loading');
            alert('Server error when loading countries');
        }
    });
}

/**
 * Generate visualization based on form inputs
 */
function generateVisualization() {
    const commodityCode = $('#commodity').val();
    const startYear = $('#start-year').val();
    const endYear = $('#end-year').val();
    const countries = $('#countries').val() || ['All Countries'];
    const metric = $('#metric').val();
    const plotType = $('#plot-type').val();

    if (commodityCode && startYear && endYear && metric && plotType) {
        showLoading('loading');
        $('#plot-container').empty();
        $('#summary-container').hide();

        $.ajax({
            url: '/weekly_export_sales/get_plot',
            type: 'POST',
            data: {
                commodity_code: commodityCode,
                start_year: startYear,
                end_year: endYear,
                'countries[]': countries,
                metric: metric,
                plot_type: plotType
            },
            success: function(response) {
                hideLoading('loading');

                if (response.success) {
                    // Display the plot
                    const plotJson = JSON.parse(response.plot);
                    Plotly.newPlot('plot-container', plotJson.data, plotJson.layout, {
                        responsive: true,
                        displayModeBar: true,
                        displaylogo: false,
                        modeBarButtonsToRemove: ['lasso2d', 'select2d']
                    });

                    // Update summary
                    updateSummary(response.summary, response.commodity, countries);
                } else {
                    showNoDataMessage(response.error || 'No data available for the selected parameters');
                }
            },
            error: function() {
                hideLoading('loading');
                showError('plot-container', 'An error occurred while generating the plot. Please try again later.');
            }
        });
    } else {
        alert('Please fill in all required fields');
    }
}

/**
 * Update the summary information display
 * @param {Object} summary - Summary data
 * @param {Object} commodity - Commodity information
 * @param {Array} countries - Selected countries
 */
function updateSummary(summary, commodity, countries) {
    let countryText = 'All Countries';
    if (countries.length === 1 && countries[0] !== 'All Countries') {
        countryText = countries[0];
    } else if (countries.length > 1) {
        countryText = `${countries.length} Selected Countries`;
    }

    const summaryHtml = `
        <div class="row">
            <div class="col-md-6">
                <p><strong>Commodity:</strong> ${commodity.name}</p>
                <p><strong>Countries:</strong> ${countryText}</p>
            </div>
            <div class="col-md-6">
                <p><strong>Latest Week:</strong> ${formatNumber(summary.latest_week)} ${summary.units}</p>
                <p><strong>Last Updated:</strong> ${formatDate(summary.latest_date)}</p>
            </div>
        </div>
    `;

    $('#summary-content').html(summaryHtml);
    $('#summary-container').show();
}

/**
 * Display a no data message in the plot container
 * @param {string} message - Error message
 */
function showNoDataMessage(message) {
    $('#plot-container').html(`
        <div class="alert alert-warning">
            <h4>No Data Available</h4>
            <p>${message}</p>
            <p>Try changing your selection criteria.</p>
        </div>
    `);
}

/**
 * Reset the year dropdowns to their default state
 */
function resetYearDropdowns() {
    $('#start-year, #end-year').html('<option value="">Select Year</option>').prop('disabled', true);
}

/**
 * Disable form controls
 */
function disableControls() {
    $('#update-countries').prop('disabled', true);
    $('#countries').html('<option value="All Countries" selected>All Countries</option>').prop('disabled', true);
    $('#update-plot').prop('disabled', true);
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
 * Format date string
 * @param {string} dateString - Date string to format
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    if (dateString === 'N/A') return 'N/A';
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}