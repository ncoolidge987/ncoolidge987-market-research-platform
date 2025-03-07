"""
Configuration for the Weekly Export Sales data collector.
Contains settings specific to USDA Export Sales data collection.
"""

import os
import sys

# Add the project root to the Python path if running standalone
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data_collectors.config import CollectorConfig

class WeeklyExportCollectorConfig(CollectorConfig):
    """Configuration for Weekly Export Sales data collector."""
    
    # Module-specific paths
    MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(CollectorConfig.DATA_DIR, 'weekly_export_sales', 'weekly_export_sales.db')
    LOG_PATH = os.path.join(CollectorConfig.COLLECTOR_LOGS_DIR, 'weekly_export_sales.log')
    
    # API settings
    BASE_URL = "https://api.fas.usda.gov/api/esr"
    API_KEYS = [
        "sXXbup7bXhySZZJBQv5VmmugtL3iW1UoRyjfeHJX",
        "O3NXAWRBr9DTb9EzpgzXcfB0FDhUWnyWSMZaT21u",
        "7eZV4w04Gpwd44zqOKoB92Is9nLwNdtTqqThNqPq",
        "P5cCtban45muGHzXVI9dgrdpnyCuQ1ogyJioOlgo",
        "H6UpwAmkElhx1Vjv3N3f0aBcBGND5KekrBTEXoFP"
    ]
    RATE_LIMIT_THRESHOLD = 50
    
    # Request settings
    TIMEOUT = 120
    RETRY_DELAY = 5
    
    # Ensure module-specific directories exist
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist."""
        super().ensure_directories()
        os.makedirs(os.path.dirname(cls.DB_PATH), exist_ok=True)