"""
Utility functions for the Weekly Export Sales module.
Contains helper functions for data visualization and processing.
"""

import pandas as pd
from typing import Union, Optional
from datetime import datetime
import plotly.graph_objects as go

def calculate_weeks_into_my(date: Union[str, datetime, pd.Timestamp], 
                       my_start_date: Union[str, datetime, pd.Timestamp]) -> Optional[int]:
    """
    Calculate the number of weeks between a date and the marketing year start date.
    
    Args:
        date: The date to calculate weeks for
        my_start_date: The marketing year start date
        
    Returns:
        int: Number of weeks into the marketing year, or None if inputs are invalid
    """
    if pd.isna(date) or pd.isna(my_start_date):
        return None
    
    # Convert string dates to datetime if needed
    if isinstance(date, str):
        date = pd.to_datetime(date)
    
    if isinstance(my_start_date, str):
        my_start_date = pd.to_datetime(my_start_date)
        
    # Calculate weeks difference
    days_diff = (date - my_start_date).days
    
    # If date is more than one year before start, return None
    if days_diff < -368:
        return None
        
    # Calculate weeks (integer division)
    weeks = days_diff // 7 
    
    return weeks


def calculate_weeks_into_my_for_df(df: pd.DataFrame, 
                                 date_col: str = 'weekEndingDate', 
                                 my_start_col: str = 'marketYearStart',
                                 result_col: str = 'weeks_into_my') -> pd.DataFrame:
    """
    Add a column to a DataFrame with the number of weeks into marketing year.
    
    Args:
        df: DataFrame containing date and marketing year start columns
        date_col: Name of the column containing the date
        my_start_col: Name of the column containing the marketing year start date
        result_col: Name of the column to store the result
        
    Returns:
        pd.DataFrame: DataFrame with the new column added
    """
    result_df = df.copy()
    
    # Apply the calculation to each row
    result_df[result_col] = result_df.apply(
        lambda row: calculate_weeks_into_my(row[date_col], row[my_start_col]),
        axis=1
    )
    
    return result_df


def create_weekly_plot(data, metric, metric_name, units, start_year, end_year, countries):
    """Create a weekly trend plot."""
    if data.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig

    fig = go.Figure()
    for year in sorted(data['market_year'].unique()):
        year_data = data[data['market_year'] == year]
        fig.add_trace(go.Bar(
            x=year_data['weekEndingDate'],
            y=year_data[metric],
            name=f'MY {year-1}/{year}'
        ))

    title_suffix = ""
    if countries and "All Countries" not in countries:
        title_suffix = f" - {', '.join(countries) if len(countries) <= 3 else f'{len(countries)} Countries'}"

    fig.update_layout(
        title=f'{metric_name} - Weekly Trend (MY {start_year}-{end_year}){title_suffix}',
        xaxis_title='Week Ending Date',
        yaxis_title=units,
        showlegend=True,
        height=700,
        width=1000,
        template='plotly_white',
        barmode='overlay',
        legend=dict(
            x=1.05,
            y=1,
            xanchor='left',
            yanchor='top',
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='black',
            borderwidth=1,
            font=dict(size=10),
            traceorder='normal',
            itemsizing='constant',
            itemwidth=30,
            orientation='v',
            tracegroupgap=0
        ),
        margin=dict(l=50, r=150, t=100, b=50)
    )
    return fig

def create_country_plot(data, metric, metric_name, units, start_year, end_year, countries):
    """Create a plot showing data by country."""
    if data.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig

    fig = go.Figure()
    for country in sorted(data['countryName'].unique()):
        country_data = data[data['countryName'] == country]
        fig.add_trace(go.Bar(
            x=country_data['weekEndingDate'],
            y=country_data[metric],
            name=country
        ))

    title_suffix = ""
    if countries and "All Countries" not in countries:
        title_suffix = f" - {', '.join(countries) if len(countries) <= 3 else f'{len(countries)} Countries'}"

    fig.update_layout(
        title=f'{metric_name} - Weekly Trend by Country (MY {start_year}-{end_year}){title_suffix}',
        xaxis_title='Week Ending Date',
        yaxis_title=units,
        showlegend=True,
        height=700,
        width=1000,
        template='plotly_white',
        barmode='stack',
        legend=dict(
            x=1.05,
            y=1,
            xanchor='left',
            yanchor='top',
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='black',
            borderwidth=1,
            font=dict(size=10),
            traceorder='normal',
            itemsizing='constant',
            itemwidth=30,
            orientation='v',
            tracegroupgap=0
        ),
        margin=dict(l=50, r=150, t=100, b=50)
    )
    return fig

def create_my_comparison_plot(data, metric, metric_name, units, start_year, end_year, countries):
    """Create a marketing year comparison plot."""
    fig = go.Figure()

    if not data:
        fig.update_layout(title="No data available")
        return fig

    for year, year_data in data.items():
        df = year_data['data']
        start_date = year_data['start_date']

        start_date_str = start_date.strftime('%b %d') if start_date is not None else 'Unknown'

        fig.add_trace(go.Scatter(
            x=df['weeks_into_my'],
            y=df[metric],
            name=f'MY {year-1}/{year} (Start: {start_date_str})',
            mode='lines'
        ))

    title_suffix = ""
    if countries and "All Countries" not in countries:
        title_suffix = f" - {', '.join(countries) if len(countries) <= 3 else f'{len(countries)} Countries'}"

    fig.update_layout(
        title=f'Weekly {metric_name} - Marketing Year Comparison{title_suffix}',
        xaxis_title='Weeks into Marketing Year',
        yaxis_title=f'{units}',
        showlegend=True,
        height=700,
        width=1000,
        template='plotly_white',
        xaxis=dict(tickmode='linear', dtick=4),
        legend=dict(
            x=1.05,
            y=1,
            xanchor='left',
            yanchor='top',
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='black',
            borderwidth=1,
            font=dict(size=10),
            traceorder='normal',
            itemsizing='constant',
            itemwidth=30,
            orientation='v',
            tracegroupgap=0
        ),
        margin=dict(l=50, r=150, t=100, b=50)
    )
    return fig