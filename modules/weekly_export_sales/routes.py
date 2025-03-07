"""
Route definitions for the Weekly Export Sales module.
Handles both visualization and report endpoints.
"""

import logging
import json
import pandas as pd
import plotly
import plotly.graph_objects as go
from flask import render_template, request, jsonify, current_app, Blueprint

# Access the blueprint through circular import workaround
def get_blueprint():
    from flask import current_app
    return current_app.blueprints['weekly_export_sales']

def get_data_manager():
    bp = get_blueprint()
    return bp.export_manager

from .utils import create_weekly_plot, create_country_plot, create_my_comparison_plot
from . import weekly_exports_bp
# ===== Visualization Routes =====

@weekly_exports_bp.route('/')
def weekly_export_sales():
    """Main page for Weekly Export Sales visualization and reports."""
    active_tab = request.args.get('tab', 'visualization')
    
    if active_tab == 'visualization':
        data_manager = get_data_manager()
        commodities = data_manager.get_commodities().to_dict('records')
        return render_template(
            'interactive_visual.html',
            active_tab=active_tab,
            commodities=commodities
        )
    else:
        # Redirect to the report page
        return render_template('report.html')

@weekly_exports_bp.route('/get_years', methods=['POST'])
def esr_get_years():
    """Get available marketing years for a selected commodity."""
    data_manager = get_data_manager()
    commodity_code = int(request.form.get('commodity_code'))
    try:
        years_df = data_manager.get_marketing_year_info(commodity_code)
        years = sorted(years_df['marketYear'].tolist())
        return jsonify({
            'success': True,
            'years': years,
            'min_year': min(years),
            'max_year': max(years)
        })
    except Exception as e:
        logging.error(f"Error getting years: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@weekly_exports_bp.route('/get_countries', methods=['POST'])
def esr_get_countries():
    """Get countries with available data for selected commodity and years."""
    data_manager = get_data_manager()
    commodity_code = int(request.form.get('commodity_code'))
    start_year = int(request.form.get('start_year'))
    end_year = int(request.form.get('end_year'))

    try:
        countries = data_manager.get_countries_with_data(commodity_code, start_year, end_year)
        return jsonify({
            'success': True,
            'countries': countries
        })
    except Exception as e:
        logging.error(f"Error getting countries: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@weekly_exports_bp.route('/get_plot', methods=['POST'])
def esr_get_plot():
    """Generate visualization based on user parameters."""
    data_manager = get_data_manager()
    commodity_code = int(request.form.get('commodity_code'))
    start_year = int(request.form.get('start_year'))
    end_year = int(request.form.get('end_year'))
    metric = request.form.get('metric')
    plot_type = request.form.get('plot_type')
    countries = request.form.getlist('countries[]')

    if 'All Countries' in countries:
        countries = ["All Countries"]

    try:
        # Load data
        data = data_manager.load_data(commodity_code, start_year, end_year)

        if data.empty:
            return jsonify({
                'success': False,
                'error': 'No data available for the selected parameters'
            })

        # Get summary data
        summary = data_manager.get_summary_data(data, metric, countries)

        # Create plot based on type
        if plot_type == 'weekly':
            plot_data = data_manager.get_weekly_data(data, metric, countries)
            fig = create_weekly_plot(plot_data, metric, data_manager.metrics[metric],
                                    summary['units'], start_year, end_year, countries)
        elif plot_type == 'country':
            plot_data = data_manager.get_weekly_data_by_country(data, metric, countries)
            fig = create_country_plot(plot_data, metric, data_manager.metrics[metric],
                                     summary['units'], start_year, end_year, countries)
        else:  # 'my_comparison'
            plot_data = data_manager.get_marketing_year_data(data, metric, countries, start_year, end_year)
            fig = create_my_comparison_plot(plot_data, metric, data_manager.metrics[metric],
                                          summary['units'], start_year, end_year, countries)

        # Convert plot to JSON
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Get commodity information
        unit_info = data_manager.get_unit_info(commodity_code)

        return jsonify({
            'success': True,
            'plot': plot_json,
            'summary': summary,
            'commodity': {
                'name': unit_info['commodity_name'],
                'unit': unit_info['unit_name']
            }
        })
    except Exception as e:
        logging.error(f"Error generating plot: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

# ===== Report Routes =====

@weekly_exports_bp.route('/report')
def export_report():
    """Dedicated route for Weekly Export Sales reports."""
    data_manager = get_data_manager()
    commodities = data_manager.get_commodities().to_dict('records')
    return render_template(
        'report.html',
        commodities=commodities
    )

@weekly_exports_bp.route('/generate_report', methods=['POST'])
def esr_generate_report():
    """Generate a structured report for Weekly Export Sales."""
    data_manager = get_data_manager()
    commodity_code = int(request.form.get('commodity_code'))
    report_type = request.form.get('report_type', 'weekly')

    try:
        # Get commodity information
        commodity_info = data_manager.get_unit_info(commodity_code)
        
        # Generate report based on type
        if report_type == 'weekly':
            report_data = {
                'commodity_info': commodity_info,
                'report_date': None,
                'report_type': 'weekly',
                'data_available': False,
                'message': 'This is a placeholder for the weekly report. Full implementation coming soon.'
            }
        elif report_type == 'monthly':
            report_data = {
                'report_type': 'monthly',
                'data_available': False,
                'message': 'Monthly report generation will be implemented in a future update.'
            }
        elif report_type == 'yearly':
            report_data = {
                'report_type': 'yearly',
                'data_available': False,
                'message': 'Marketing Year report generation will be implemented in a future update.'
            }
        else:
            report_data = {'error': f'Unknown report type: {report_type}'}
            
        return jsonify({
            'success': True,
            'report': report_data
        })
    except Exception as e:
        logging.error(f"Error generating report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })