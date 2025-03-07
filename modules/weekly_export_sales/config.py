"""
Configuration settings specific to the Weekly Export Sales web module
"""

import os
from config import Config

class WeeklyExportConfig:
    """Configuration for the Weekly Export Sales web module."""
    
    # Base directory of the module
    MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Path to SQLite database
    DB_PATH = os.path.join(Config.DATA_DIR, 'weekly_export_sales', 'weekly_export_sales.db')
    
    # UI Settings
    DEFAULT_METRIC = 'weeklyExports'
    DEFAULT_PLOT_TYPE = 'weekly'
    
    # Metrics mapping (used for display)
    METRICS = {
        'weeklyExports': 'Weekly Exports',
        'accumulatedExports': 'Accumulated Exports',
        'outstandingSales': 'Outstanding Sales',
        'grossNewSales': 'Gross New Sales',
        'netSales': 'Net Sales',
        'totalCommitment': 'Total Commitment'
    }
    
    # Ensure the data directory exists
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        os.makedirs(os.path.dirname(cls.DB_PATH), exist_ok=True)