"""
Global configuration settings for the Market Research Platform
This file contains only the essential global configuration settings.
Module-specific settings are kept in their respective config.py files.
"""

import os

class Config:
    """Base configuration for the main application."""
    
    # Base directory of the application
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    
    # Path definitions
    DATA_DIR = os.path.join(BASEDIR, 'data')
    LOGS_DIR = os.path.join(BASEDIR, 'logs')