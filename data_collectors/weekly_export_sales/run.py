#!/usr/bin/env python
"""
Weekly Export Sales Data Collection Script
This script runs the data collection process for USDA Weekly Export Sales data.
It can be executed directly or scheduled via cron.

Example cron entry (runs every Thursday at 1:00 AM):
0 1 * * 4 /path/to/market_research_platform/data_collectors/weekly_export_sales/run.py

Make sure to set execution permissions:
chmod +x /path/to/market_research_platform/data_collectors/weekly_export_sales/run.py
"""

import os
import sys
import logging
from datetime import datetime

# Ensure proper imports when run as script
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data_collectors.weekly_export_sales.collector import collect_data
from data_collectors.weekly_export_sales.config import WeeklyExportCollectorConfig

def main():
    """Main function to run the data collection process."""
    # Ensure directories exist
    WeeklyExportCollectorConfig.ensure_directories()
    
    # Configure logging for direct execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=WeeklyExportCollectorConfig.LOG_PATH,
        filemode='a'
    )
    
    logging.info(f"=== Starting Weekly Export Sales data collection at {datetime.now()} ===")
    
    try:
        collect_data()
        logging.info(f"=== Weekly Export Sales data collection completed successfully at {datetime.now()} ===")
        return 0
    except Exception as e:
        logging.error(f"=== Weekly Export Sales data collection failed at {datetime.now()}: {str(e)} ===")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)