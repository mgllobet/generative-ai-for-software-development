/**
 * ============================================================================
 * WORLD TOUR WIDGET - CONFIGURATION FILE
 * ============================================================================
 *
 * This file controls the appearance and behavior of your World Tour Widget.
 *
 * HOW TO CUSTOMIZE WITH AN LLM (ChatGPT, Claude, etc.):
 *
 * 1. Copy this ENTIRE file
 * 2. Paste it to your LLM with instructions like:
 *    - "Add dark mode toggle functionality"
 *    - "Change the color scheme to ocean blue theme"
 *    - "Show 6 alternative routes instead of 4"
 *    - "Add a button to export routes to CSV"
 *    - "Change all text to Spanish"
 *
 * 3. The LLM will return an improved version
 * 4. Copy the improved code back to this file
 * 5. Save the file
 * 6. Restart your Flask server (Ctrl+C, then re-run notebook cell)
 * 7. Refresh browser - changes appear!
 *
 * TIPS FOR BEST LLM RESULTS:
 * - Be specific: "Change primary color to #0066cc" instead of "make it blue"
 * - Ask for one change at a time
 * - Tell the LLM to preserve existing features you want to keep
 * - If something breaks, paste the error message to the LLM
 *
 * ============================================================================
 */

const WIDGET_CONFIG = {

    // ========================================================================
    // THEME COLORS
    // ========================================================================
    // Controls the color scheme of the entire widget
    //
    // Example LLM prompts:
    // - "Change to a green nature theme"
    // - "Make it match my university colors: blue #003366 and gold #FFD700"
    // - "Create a high-contrast theme for accessibility"
    // ========================================================================

    theme: {
        // Main colors (light mode)
        primaryColor: '#667eea',        // Purple - used for buttons, highlights
        secondaryColor: '#764ba2',      // Darker purple - used for gradients
        backgroundColor: '#ffffff',      // White - main background
        textColor: '#333333',           // Dark gray - main text
        accentColor: '#f093fb',         // Pink - used for stats, special elements
        borderColor: '#e0e0e0',         // Light gray - borders and dividers

        // Dark mode colors (optional)
        // Set darkMode.enabled to true to activate
        darkMode: {
            enabled: false,              // Change to true to enable dark mode
            primaryColor: '#8b9dc3',     // Lighter purple for dark backgrounds
            secondaryColor: '#9a7db8',   // Lighter secondary color
            backgroundColor: '#1a1a1a',  // Very dark gray - main background
            textColor: '#e0e0e0',        // Light gray - main text
            accentColor: '#ff6b9d',      // Brighter pink for visibility
            borderColor: '#444444'       // Medium gray - borders
        }
    },

    // ========================================================================
    // FEATURES & FUNCTIONALITY
    // ========================================================================
    // Enable/disable features and control their behavior
    //
    // Example LLM prompts:
    // - "Show 8 alternative routes instead of 4"
    // - "Add a dark mode toggle button at the top"
    // - "Disable the distance display, only show prices"
    // - "Add smooth fade-in animations"
    // ========================================================================

    features: {
        // Shortest Path features
        alternativeRoutes: 4,            // Number of route alternatives to show (1-10)
        showDistance: true,              // Show distance in kilometers
        showPrice: true,                 // Show flight prices
        showFlightCount: true,           // Show number of flights (stops)

        // User interface features
        enableDarkModeToggle: false,     // Show dark/light mode toggle button
        enableExportButton: false,       // Show button to export routes to CSV
        enableShareButton: false,        // Show button to share route via URL
        enablePrintButton: false,        // Show button to print route details

        // Visual features
        animateTransitions: true,        // Smooth animations when switching modes
        animatePaths: false,             // Animate flight paths on map (slower)
        showFlags: false,                // Show country flags next to names
        highlightCheapest: true,         // Highlight the cheapest route in green

        // Map features
        zoomToRoute: true,               // Auto-zoom map to fit the route
        showRouteLabels: true            // Show "#1, #2, #3" labels on countries
    },

    // ========================================================================
    // TEXT & LABELS
    // ========================================================================
    // Customize all text displayed in the widget
    //
    // Example LLM prompts:
    // - "Translate all text to Spanish"
    // - "Make the language more casual and friendly"
    // - "Add emojis to all buttons"
    // - "Change 'Compute Optimal Tour' to 'Plan My Trip'"
    // ========================================================================

    text: {
        // Main titles
        pageTitle: '🌍 World Tour & Flight Finder',
        shortestPathTitle: '✈️ Shortest Path (Cheapest Flights)',
        tourTitle: '🗺️ Tour Planning (TSP)',

        // Info messages
        shortestPathInfo: 'Find the cheapest flight route between two countries. Direct flights aren\'t always cheapest!',
        tourInfo: 'Plan an optimal tour visiting multiple countries. Uses geographic distance, not flight prices.',

        // Buttons
        findPathButton: 'Find Cheapest Route',
        computeTourButton: 'Compute Optimal Tour',
        selectAllButton: 'Select All',
        clearAllButton: 'Clear All',
        darkModeButton: '🌙 Dark Mode',
        lightModeButton: '☀️ Light Mode',
        exportButton: '📥 Export Route',
        shareButton: '🔗 Share',
        printButton: '🖨️ Print',

        // Labels
        fromCountryLabel: 'From Country',
        toCountryLabel: 'To Country',
        startCountryLabel: 'Starting Country',
        selectCountriesLabel: 'Select Countries',

        // Results
        alternativeRoutesTitle: '✈️ Alternative Routes Found',
        routeDetailsTitle: '📋 Flight Route Details',
        tourRouteTitle: '📋 Tour Route',
        flightsLabel: 'Flights:',
        countriesLabel: 'Countries:',
        continentsLabel: 'Continents:',
        totalCostLabel: 'Total Cost:',

        // Route badges
        cheapestBadge: 'CHEAPEST',
        alternativeBadge: 'ALT',

        // Status messages
        loadingMessage: 'Loading...',
        computingMessage: 'Computing...',
        noPathFound: 'No path found between these countries',
        errorMessage: 'An error occurred. Please try again.',

        // Placeholders
        selectStartPlaceholder: 'Select starting country...',
        selectEndPlaceholder: 'Select destination country...',
        selectTourStartPlaceholder: 'Select start country...'
    },

    // ========================================================================
    // MAP SETTINGS
    // ========================================================================
    // Customize the interactive map appearance
    //
    // Example LLM prompts:
    // - "Make flight paths blue instead of red"
    // - "Use larger markers for countries"
    // - "Change map projection to Mercator"
    // - "Make the lines thicker and more visible"
    // ========================================================================

    map: {
        // Map projection type
        // Options: 'natural earth', 'mercator', 'orthographic', 'equirectangular'
        projection: 'natural earth',

        // Flight path styling
        pathColor: 'rgba(255, 0, 0, 0.6)',  // Red with transparency
        pathWidth: 2,                        // Line thickness in pixels
        pathStyle: 'solid',                  // 'solid', 'dashed', or 'dotted'

        // Country marker styling
        markerSize: 10,                      // Size of country markers
        markerColor: 'red',                  // Color of country markers
        markerSymbol: 'circle',              // 'circle', 'square', 'diamond', 'cross'

        // Label styling (for #1, #2, #3 position markers)
        labelSize: 9,                        // Font size for position numbers
        labelColor: 'darkblue',              // Color of position numbers
        labelPosition: 'top center',         // Where to place labels relative to markers

        // Map colors
        landColor: 'lightgray',              // Color of land masses
        oceanColor: 'lightblue',             // Color of oceans
        countryBorderColor: 'white',         // Color of country borders

        // Map dimensions
        height: 750,                         // Map height in pixels

        // Background
        backgroundColor: 'white'             // Background color around the map
    },

    // ========================================================================
    // LAYOUT & SIZING
    // ========================================================================
    // Control the layout and spacing of UI elements
    //
    // Example LLM prompts:
    // - "Make the sidebar wider to show more country names"
    // - "Reduce padding to fit more on screen"
    // - "Make buttons bigger for touch screens"
    // ========================================================================

    layout: {
        // Main container
        containerMaxWidth: '1400px',         // Maximum width of entire widget
        sidebarWidth: '400px',               // Width of left sidebar with controls

        // Spacing
        sectionSpacing: '20px',              // Space between major sections
        elementSpacing: '12px',              // Space between small elements
        padding: '20px',                     // Internal padding

        // Font sizes
        titleFontSize: '1.4em',              // Size of section titles
        bodyFontSize: '0.9em',               // Size of regular text
        buttonFontSize: '1.05em',            // Size of button text

        // Button styling
        buttonHeight: '45px',                // Height of main buttons
        buttonRadius: '8px',                 // Border radius (roundness)

        // Input styling
        inputHeight: '40px',                 // Height of dropdowns/inputs
        inputRadius: '6px'                   // Border radius for inputs
    },

    // ========================================================================
    // ADVANCED SETTINGS
    // ========================================================================
    // Advanced customization for power users
    // Most learners won't need to change these
    //
    // Example LLM prompts:
    // - "Increase the route comparison table row height"
    // - "Change the loading spinner color"
    // - "Add a custom CSS class for styling"
    // ========================================================================

    advanced: {
        // API request timeout
        apiTimeout: 30000,                   // Milliseconds before request times out

        // Animation durations
        transitionDuration: '0.3s',          // How long transitions take

        // Table settings
        tableRowHeight: '45px',              // Height of route comparison rows
        tableHeaderHeight: '50px',           // Height of table headers

        // Loading spinner
        spinnerColor: '#667eea',             // Color of loading spinner
        spinnerSize: '40px',                 // Size of loading spinner

        // Debug mode
        debugMode: false,                    // Set to true to show console logs

        // Custom CSS classes (for advanced styling)
        customClasses: {
            container: '',                   // Add custom class to main container
            sidebar: '',                     // Add custom class to sidebar
            map: ''                          // Add custom class to map container
        }
    }
};

/**
 * ============================================================================
 * END OF CONFIGURATION
 * ============================================================================
 *
 * Don't edit below this line unless you know JavaScript!
 *
 * The code below makes the config available to the widget.
 * ============================================================================
 */

// Make config globally available
if (typeof window !== 'undefined') {
    window.WIDGET_CONFIG = WIDGET_CONFIG;
}
