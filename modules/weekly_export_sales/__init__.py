"""
Weekly Export Sales Module
This module provides data visualization and reporting functionality
for USDA Weekly Export Sales data.
"""

from flask import Blueprint

# Create the blueprint first
weekly_exports_bp = Blueprint(
    'weekly_export_sales',
    __name__,
    url_prefix='/weekly_export_sales',
    template_folder='templates',
    static_folder='static'
)

# Attach the data manager to the blueprint
from .config import WeeklyExportConfig
from .manager import ExportDataManager
weekly_exports_bp.export_manager = ExportDataManager(WeeklyExportConfig.DB_PATH)

# Import routes AFTER creating the blueprint to avoid circular imports
from . import routes

def create_module():
    """Create and configure the Weekly Export Sales blueprint."""
    return weekly_exports_bp

__version__ = '1.0.0'