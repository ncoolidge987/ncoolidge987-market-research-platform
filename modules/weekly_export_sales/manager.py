"""
Data manager for the Weekly Export Sales web module.
Handles database interactions and data processing for visualization.
"""

import os
import logging
import sqlite3
import pandas as pd
from typing import List, Dict, Optional
from .config import WeeklyExportConfig
from .utils import calculate_weeks_into_my, calculate_weeks_into_my_for_df

class ExportDataManager:
    """Data manager class for export sales data, handling database operations."""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or WeeklyExportConfig.DB_PATH
        self._ensure_db_directory()
        self.metrics = WeeklyExportConfig.METRICS
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def get_commodities(self) -> pd.DataFrame:
        """Get all available commodities."""
        with self.get_connection() as conn:
            return pd.read_sql("""
                SELECT commodityCode, commodityName
                FROM metadata_commodities
                ORDER BY commodityName
            """, conn)

    def get_countries(self) -> pd.DataFrame:
        """Get all available countries."""
        with self.get_connection() as conn:
            return pd.read_sql("""
                SELECT DISTINCT countryCode, countryName
                FROM metadata_countries
                ORDER BY countryName
            """, conn)

    def get_countries_with_data(self, commodity_code: int, start_my: int, end_my: int) -> List[str]:
        """Get countries that have data for the selected commodity and marketing years."""
        with self.get_connection() as conn:
            df = pd.read_sql("""
                SELECT
                    mc.countryName,
                    SUM(COALESCE(e.weeklyExports, 0)) as total_exports
                FROM commodity_exports e
                JOIN metadata_countries mc ON e.countryCode = mc.countryCode
                WHERE e.commodityCode = ?
                AND e.market_year BETWEEN ? AND ?
                GROUP BY mc.countryName
                ORDER BY total_exports DESC
            """, conn, params=(commodity_code, start_my, end_my))

            return df['countryName'].tolist()
            
    def get_marketing_year_info(self, commodity_code: int) -> pd.DataFrame:
        """Get marketing year information for a commodity."""
        with self.get_connection() as conn:
            my_dates = pd.read_sql("""
                SELECT
                    marketYear,
                    marketYearStart,
                    marketYearEnd
                FROM data_releases
                WHERE commodityCode = ?
                ORDER BY marketYear
            """, conn, params=(commodity_code,))

            if my_dates.empty:
                raise ValueError(f"No marketing year data for commodity {commodity_code}")

            my_dates['marketYearStart'] = pd.to_datetime(my_dates['marketYearStart'])
            my_dates['marketYearEnd'] = pd.to_datetime(my_dates['marketYearEnd'])

            latest_year = my_dates['marketYear'].max()
            latest_year_data = my_dates[my_dates['marketYear'] == latest_year].iloc[0]

            next_year_data = pd.DataFrame({
                'marketYear': [latest_year + 1],
                'marketYearStart': [latest_year_data['marketYearStart'] + pd.offsets.DateOffset(years=1)],
                'marketYearEnd': [latest_year_data['marketYearEnd'] + pd.offsets.DateOffset(years=1)]
            })

            return pd.concat([my_dates, next_year_data], ignore_index=True)
            
    def get_unit_info(self, commodity_code: int) -> dict:
        """Get unit information for a commodity."""
        with self.get_connection() as conn:
            info = pd.read_sql("""
                SELECT
                    m.commodityCode,
                    m.commodityName,
                    m.unitId,
                    u.unitNames
                FROM metadata_commodities m
                JOIN metadata_units u ON m.unitId = u.unitId
                WHERE m.commodityCode = ?
            """, conn, params=(commodity_code,))

            if info.empty:
                raise ValueError(f"No commodity found with code {commodity_code}")

            return {
                'commodity_code': info['commodityCode'].iloc[0],
                'commodity_name': info['commodityName'].iloc[0],
                'unit_id': info['unitId'].iloc[0],
                'unit_name': info['unitNames'].iloc[0]
            }

    def load_data(self, commodity_code: int, start_my: int, end_my: int) -> pd.DataFrame:
        """Load export data for a commodity and time period."""
        my_dates = self.get_marketing_year_info(commodity_code)
        unit_info = self.get_unit_info(commodity_code)
        
        # Validate marketing years
        if start_my > end_my:
            raise ValueError("Start marketing year must be <= end marketing year")
        if not all(my in my_dates['marketYear'].values for my in range(start_my, end_my + 1)):
            raise ValueError("Some specified marketing years not found in database")
        
        with self.get_connection() as conn:
            exports_df = pd.read_sql("""
                SELECT
                    e.*,
                    c.commodityName,
                    mc.countryName,
                    mc.countryDescription,
                    mc.regionId,
                    u.unitNames as unit
                FROM commodity_exports e
                JOIN metadata_commodities c ON e.commodityCode = c.commodityCode
                JOIN metadata_countries mc ON e.countryCode = mc.countryCode
                JOIN metadata_units u ON e.unitId = u.unitId
                WHERE e.commodityCode = ?
                AND e.market_year BETWEEN ? AND ?
                ORDER BY weekEndingDate
            """, conn, params=(commodity_code, start_my, end_my))

        if exports_df.empty:
            logging.warning(f"No export data for commodity {commodity_code} in years {start_my}-{end_my}")
            return pd.DataFrame()

        exports_df['weekEndingDate'] = pd.to_datetime(exports_df['weekEndingDate'])

        column_mappings = {
            'current': {
                'netSales': 'currentMYNetSales',
                'totalCommitment': 'currentMYTotalCommitment',
                'outstandingSales': 'outstandingSales',
                'accumulatedExports': 'accumulatedExports',
                'weeklyExports': 'weeklyExports',
                'grossNewSales': 'grossNewSales'
            },
            'next': {
                'netSales': 'nextMYNetSales',
                'outstandingSales': 'nextMYOutstandingSales',
            }
        }

        # Make a temporary copy to pre-calculate week numbers for marketing year transitions
        temp_df = exports_df.copy()

        # Join with marketing year dates
        temp_df = temp_df.merge(my_dates, left_on='market_year', right_on='marketYear', how='left')

        # Calculate weeks into marketing year using our utility function
        temp_df = calculate_weeks_into_my_for_df(temp_df)

        # Process current marketing year data
        current_my_data = exports_df.drop(columns=list(column_mappings['next'].values()), errors='ignore')
        for std_col, source_col in column_mappings['current'].items():
            if source_col in current_my_data.columns and std_col != source_col:
                current_my_data[std_col] = current_my_data[source_col]
        current_my_data = current_my_data.drop(columns=[col for std_col, col in column_mappings['current'].items()
                                            if std_col != col and col in current_my_data.columns],
                                            errors='ignore')

        # Process next marketing year data
        next_my_data = exports_df.copy()

        # Join next_my_data with temp_df to get the weeks_into_my column
        next_my_data = next_my_data.merge(
            temp_df[['weekEndingDate', 'market_year', 'countryCode', 'weeks_into_my']],
            on=['weekEndingDate', 'market_year', 'countryCode'],
            how='left'
        )

        # For week 1 data, only keep rows that have meaningful next MY data
        week_one_data = next_my_data[next_my_data['weeks_into_my'] == 1]
        other_weeks_data = next_my_data[next_my_data['weeks_into_my'] != 1]

        # For week 1, we'll be selective about which data to keep
        filtered_week_one = week_one_data.copy()
        for _, source_col in column_mappings['next'].items():
            if source_col in filtered_week_one.columns:
                # Keep rows where next MY data is meaningful (not null and not zero)
                mask = pd.notna(filtered_week_one[source_col]) & (filtered_week_one[source_col] != 0)
                filtered_week_one = filtered_week_one[mask]

        # Recombine with other weeks data
        next_my_data = pd.concat([filtered_week_one, other_weeks_data], ignore_index=True)

        # Drop the current marketing year columns and weeks_into_my
        next_my_data = next_my_data.drop(columns=['weeks_into_my'] +
                                        [col for col in list(column_mappings['current'].values())
                                        if col in next_my_data.columns],
                                        errors='ignore')

        # Continue with normal processing for next MY data
        for std_col, source_col in column_mappings['next'].items():
            if source_col in next_my_data.columns and std_col != source_col:
                next_my_data[std_col] = next_my_data[source_col]

        next_my_data = next_my_data.drop(columns=[col for std_col, col in column_mappings['next'].items()
                                        if std_col != col and col in next_my_data.columns],
                                        errors='ignore')

        # Adjust the marketing year for next MY data
        next_my_data['market_year'] = next_my_data['market_year'] + 1

        # Combine current and next MY data
        processed_data = pd.concat([current_my_data, next_my_data], ignore_index=True)

        # Ensure no duplicates in the final dataset
        processed_data = processed_data.drop_duplicates(['weekEndingDate', 'market_year', 'countryCode'], keep='first')

        # Convert numeric columns
        numeric_columns = list(self.metrics.keys())
        for col in numeric_columns:
            if col in processed_data.columns:
                processed_data[col] = pd.to_numeric(processed_data[col], errors='coerce')

        processed_data['display_units'] = unit_info['unit_name']
        processed_data = processed_data.merge(my_dates, left_on='market_year', right_on='marketYear', how='left')

        # Calculate weeks into marketing year for final dataset using our utility function
        processed_data = calculate_weeks_into_my_for_df(processed_data)

        processed_data = processed_data.sort_values('weekEndingDate').reset_index(drop=True)
        logging.info(f"Loaded {len(processed_data)} records for commodity {commodity_code}")
        return processed_data
        
    def get_summary_data(self, df: pd.DataFrame, metric: str, countries: List[str] = None) -> Dict:
        """Get summary statistics for the specified metric and countries."""
        if df.empty:
            return {
                'latest_week': 0,
                'units': 'N/A',
                'latest_date': 'N/A'
            }

        if countries and "All Countries" not in countries:
            filtered_df = df[df['countryName'].isin(countries)]
        else:
            filtered_df = df

        if filtered_df.empty:
            return {
                'latest_week': 0,
                'units': df['display_units'].iloc[0] if not df.empty else 'N/A',
                'latest_date': 'N/A'
            }

        latest_date = filtered_df['weekEndingDate'].max()
        latest_week_df = filtered_df[filtered_df['weekEndingDate'] == latest_date]

        # Get values and convert NumPy types to Python native types
        latest_week = float(latest_week_df[metric].sum()) if metric in latest_week_df.columns else 0

        return {
            'latest_week': latest_week,
            'units': filtered_df['display_units'].iloc[0],
            'latest_date': latest_date.strftime('%Y-%m-%d') if not pd.isna(latest_date) else 'N/A'
        }
        
    def get_weekly_data(self, df: pd.DataFrame, metric: str, countries: List[str] = None) -> pd.DataFrame:
        """Get weekly aggregated data for plotting."""
        if df.empty:
            return pd.DataFrame()

        if countries and "All Countries" not in countries:
            filtered_df = df[df['countryName'].isin(countries)]
        else:
            filtered_df = df

        if filtered_df.empty:
            return pd.DataFrame()

        weekly_data = filtered_df.groupby(['market_year', 'weekEndingDate'])[metric].sum().reset_index()
        return weekly_data
        
    def get_weekly_data_by_country(self, df: pd.DataFrame, metric: str, countries: List[str] = None) -> pd.DataFrame:
        """Get weekly data by country for plotting."""
        if df.empty:
            return pd.DataFrame()

        if countries and "All Countries" not in countries:
            filtered_df = df[df['countryName'].isin(countries)]
        else:
            filtered_df = df

        if filtered_df.empty:
            return pd.DataFrame()

        weekly_data = filtered_df.groupby(['market_year', 'weekEndingDate', 'countryName'])[metric].sum().reset_index()
        return weekly_data
        
    def get_marketing_year_data(self, df: pd.DataFrame, metric: str, countries: List[str] = None, 
                               start_my: int = None, end_my: int = None) -> Dict[int, pd.DataFrame]:
        """Get data organized by weeks into marketing year for comparison."""
        if df.empty:
            return {}

        if countries and "All Countries" not in countries:
            filtered_df = df[df['countryName'].isin(countries)]
        else:
            filtered_df = df

        if filtered_df.empty:
            return {}
            
        if start_my is None or end_my is None:
            # Find min and max years in the dataframe
            start_my = filtered_df['market_year'].min()
            end_my = filtered_df['market_year'].max()

        result = {}
        max_weeks = 0

        for year in range(start_my, end_my + 1):
            year_data = filtered_df[filtered_df['market_year'] == year].copy()
            if not year_data.empty and 'weeks_into_my' in year_data.columns:
                year_data_grouped = year_data.groupby(['weeks_into_my'])[metric].sum().reset_index()

                if not year_data_grouped.empty:
                    max_weeks = max(max_weeks, int(year_data_grouped['weeks_into_my'].max()))
                    min_weeks = min(1, int(year_data_grouped['weeks_into_my'].min()))
                    all_weeks = pd.DataFrame({'weeks_into_my': range(min_weeks, max_weeks + 1)})
                    year_data_complete = pd.merge(all_weeks, year_data_grouped, on='weeks_into_my', how='left')

                    result[year] = {
                        'data': year_data_complete,
                        'start_date': year_data['marketYearStart'].iloc[0] if 'marketYearStart' in year_data.columns and not year_data['marketYearStart'].isna().all() else None
                    }

        return result