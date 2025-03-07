"""
Module registry for the Market Research Platform.
This file handles registration of all modules with the main Flask app.

Each module should:
1. Have its own blueprint definition in __init__.py
2. Be independent from other modules
3. Handle its own routes and data management
"""

def register_modules(app):
    """Register all modules with the Flask app."""
    # Import and register each module's blueprint
    from modules.weekly_export_sales import create_module
    
    # Register the Weekly Export Sales module
    weekly_exports_bp = create_module()
    app.register_blueprint(weekly_exports_bp)
    
    # Additional modules would be registered here
    # Example: 
    # from modules.another_module import create_module
    # another_module_bp = create_module()
    # app.register_blueprint(another_module_bp)