"""
Market Research Platform - Main Flask Application
This is the entry point for the Market Research Platform, which integrates
multiple data source modules.
"""

from flask import Flask, render_template, redirect, url_for
import logging
import os
from config import Config

# Import module registrations
from modules import register_modules

def create_app(config_class=Config):
    """Create and configure the Flask app."""
    # Configure logging
    os.makedirs(os.path.join(config_class.BASEDIR, 'logs', 'app'), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=os.path.join(config_class.BASEDIR, 'logs', 'app', 'app.log')
    )

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register all modules
    register_modules(app)

    # Main dashboard route
    @app.route('/')
    def index():
        """Render the main dashboard/home page."""
        return render_template('index.html')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)