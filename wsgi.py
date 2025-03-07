"""
WSGI Entry Point for the Market Research Platform # for python anywhere
"""

import sys

# Add your project directory to the Python path
path = '/home/ncoolidge/market_research_platform'
if path not in sys.path:
    sys.path.append(path)

# Import and initialize the Flask app
from app import app as application

# This variable must be named 'application'
if __name__ == '__main__':
    application.run()