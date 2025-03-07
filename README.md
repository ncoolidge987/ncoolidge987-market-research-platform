market_research_platform/
├── app.py                     # Main Flask application entry point
├── config.py                  # Global configuration settings
├── data/                      # Centralized data storage
│   └── weekly_export_sales/        # Weekly Export Sales data
│       └── weekly_export_sales.db  # SQLite database for weekly exports
├── data_collectors/           # Standalone data collection scripts
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Shared collector configuration
│   └── weekly_export_sales/        # Weekly exports collector
│       ├── __init__.py        # Package initialization
│       ├── config.py          # Collector-specific settings
│       ├── collector.py       # Data collection logic
│       └── run.py             # Executable script for scheduling
├── logs/                      # Log files directory
│   ├── app/                   # Application logs
│   │   └── app.log            # Main application log
│   └── collectors/            # Data collector logs
│       └── weekly_exports.log # Weekly exports collector log
├── modules/                   # Web application modules
│   ├── __init__.py            # Module registration
│   └── weekly_export_sales/   # Weekly Export Sales web module
│       ├── __init__.py        # Blueprint creation
│       ├── config.py          # Module-specific configuration
│       ├── manager.py         # Data retrieval and processing
│       ├── routes.py          # Route handlers
│       ├── utils.py           # Helper functions
│       ├── static/            # Module-specific static files
│       │   ├── css/           # Module CSS files
│       │   │   ├── interactive_visual.css  # Visualization page styles
│       │   │   └── report.css  # Report page styles
│       │   └── js/            # Module JavaScript files
│       │       ├── interactive_visual.js  # Visualization page scripts
│       │       └── report.js  # Report page scripts
│       └── templates/         # Module-specific templates
│           ├── interactive_visual.html  # Visualization page template
│           └── report.html    # Report page template
├── static/                    # Global static files
│   ├── css/                   # Global CSS files
│   │   └── main.css           # Main application styles
│   └── js/                    # Global JavaScript files
│       └── main.js            # Main application scripts
├── templates/                 # Global templates
│   ├── base.html              # Base template with common layout
│   └── index.html             # Main dashboard template
├── requirements.txt           # Python dependencies
└── wsgi.py                    # WSGI entry point for production
