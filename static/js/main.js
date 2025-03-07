/**
 * Main JavaScript for Market Research Platform
 * Contains global utility functions and initialization code
 */

// Wait for the document to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Setup any global event listeners
    setupGlobalListeners();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    // Check if Bootstrap's tooltip plugin is available
    if (typeof bootstrap !== 'undefined' && typeof bootstrap.Tooltip !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Set up global event listeners
 */
function setupGlobalListeners() {
    // Add any global event listeners here
    
    // Example: Listen for changes in the URL hash to update active tabs
    window.addEventListener('hashchange', handleHashChange);
    
    // Call it once to handle initial page load
    handleHashChange();
}

/**
 * Handle URL hash changes to activate the corresponding tab
 */
function handleHashChange() {
    const hash = window.location.hash;
    if (hash) {
        const tabId = hash.substring(1); // Remove the # character
        const tabElement = document.getElementById(`${tabId}-tab`);
        if (tabElement) {
            // Check if Bootstrap's Tab plugin is available
            if (typeof bootstrap !== 'undefined' && typeof bootstrap.Tab !== 'undefined') {
                const tab = new bootstrap.Tab(tabElement);
                tab.show();
            } else {
                // Fallback for manual tab activation
                const tabsList = tabElement.closest('.nav-tabs');
                if (tabsList) {
                    // Remove active class from all tabs
                    tabsList.querySelectorAll('.nav-link').forEach(link => {
                        link.classList.remove('active');
                    });
                    // Add active class to current tab
                    tabElement.classList.add('active');
                    
                    // Hide all tab content
                    const tabContent = document.querySelectorAll('.tab-content > .tab-pane');
                    tabContent.forEach(pane => {
                        pane.classList.remove('show', 'active');
                    });
                    
                    // Show current tab content
                    const currentPane = document.getElementById(tabId);
                    if (currentPane) {
                        currentPane.classList.add('show', 'active');
                    }
                }
            }
        }
    }
}

/**
 * Utility function to show a loading indicator
 * @param {string} elementClass - CSS class of the loading element to show
 */
function showLoading(elementClass = 'loading') {
    const loadingElements = document.querySelectorAll(`.${elementClass}`);
    loadingElements.forEach(element => {
        element.style.display = 'block';
    });
}

/**
 * Utility function to hide a loading indicator
 * @param {string} elementClass - CSS class of the loading element to hide
 */
function hideLoading(elementClass = 'loading') {
    const loadingElements = document.querySelectorAll(`.${elementClass}`);
    loadingElements.forEach(element => {
        element.style.display = 'none';
    });
}

/**
 * Display an error message in a container
 * @param {string} containerId - ID of the container element
 * @param {string} message - Error message to display
 */
function showError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <h4>Error</h4>
                <p>${message}</p>
            </div>
        `;
    }
}

/**
 * Format a number with commas for thousands
 * @param {number} num - Number to format
 * @returns {string} Formatted number string
 */
function formatNumber(num) {
    return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
}

/**
 * Format a date string as MM/DD/YYYY
 * @param {string} dateString - Date string to format
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    if (!dateString || dateString === 'N/A') {
        return 'N/A';
    }
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
        return 'Invalid Date';
    }
    
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}