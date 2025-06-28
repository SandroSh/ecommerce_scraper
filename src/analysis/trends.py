"""
Trend analysis module for e-commerce data.
Provides time-based trend analysis, forecasting, and pattern detection.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class TrendAnalyzer:
    """Analyze trends and patterns in e-commerce data over time."""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.logger = logging.getLogger(__name__)
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare data for trend analysis."""
        if 'createdat' in self.data.columns:
            self.data['createdat'] = pd.to_datetime(self.data['createdat'], errors='coerce')
            self.data = self.data.dropna(subset=['createdat'])
            
            # Add time-based features
            self.data['date'] = self.data['createdat'].dt.date
            self.data['hour'] = self.data['createdat'].dt.hour
            self.data['weekday'] = self.data['createdat'].dt.day_name()
            self.data['month'] = self.data['createdat'].dt.month
            self.data['week'] = self.data['createdat'].dt.isocalendar().week
        
        if 'price' in self.data.columns:
            self.data['price'] = pd.to_numeric(self.data['price'], errors='coerce')
    
    def price_trends(self) -> Dict[str, Any]:
        """Analyze price trends over time."""
        if 'price' not in self.data.columns or 'createdat' not in self.data.columns:
            return {'error': 'Price or timestamp data not available'}
        
        trends = {}
        
        # Daily price trends
        daily_prices = self.data.groupby('date')['price'].agg(['mean', 'median', 'count', 'std']).reset_index()
        daily_prices = daily_prices.dropna()
        
        if len(daily_prices) > 1:
            # Calculate trend direction
            x = np.arange(len(daily_prices))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, daily_prices['mean'])
            
            trends['daily_trends'] = {
                'trend_direction': 'increasing' if slope > 0 else 'decreasing',
                'slope': float(slope),
                'r_squared': float(r_value ** 2),
                'p_value': float(p_value),
                'is_significant': bool(p_value < 0.05),
                'daily_data': [{**record, 'date': str(record['date'])} for record in daily_prices.to_dict('records')]
            }
            
            # Price volatility analysis
            trends['volatility'] = {
                'daily_price_volatility': float(daily_prices['mean'].std()),
                'coefficient_of_variation': float(daily_prices['mean'].std() / daily_prices['mean'].mean()),
                'max_daily_change': float(daily_prices['mean'].diff().abs().max()),
                'avg_daily_change': float(daily_prices['mean'].diff().abs().mean())
            }
        
        # Category-specific price trends
        if 'category' in self.data.columns:
            category_trends = {}
            for category in self.data['category'].unique():
                cat_data = self.data[self.data['category'] == category]
                cat_daily = cat_data.groupby('date')['price'].mean().reset_index()
                
                if len(cat_daily) > 1:
                    x = np.arange(len(cat_daily))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, cat_daily['price'])
                    
                    category_trends[category] = {
                        'trend_direction': 'increasing' if slope > 0 else 'decreasing',
                        'slope': float(slope),
                        'r_squared': float(r_value ** 2),
                        'is_significant': bool(p_value < 0.05)
                    }
            
            trends['category_trends'] = category_trends
        
        return trends
    
    def volume_trends(self) -> Dict[str, Any]:
        """Analyze scraping volume trends over time."""
        if 'createdat' not in self.data.columns:
            return {'error': 'Timestamp data not available'}
        
        volume_trends = {}
        
        # Daily volume trends
        daily_counts = self.data.groupby('date').size().reset_index(name='count')
        
        if len(daily_counts) > 1:
            x = np.arange(len(daily_counts))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, daily_counts['count'])
            
            volume_trends['daily_volume'] = {
                'trend_direction': 'increasing' if slope > 0 else 'decreasing',
                'slope': float(slope),
                'r_squared': float(r_value ** 2),
                'is_significant': bool(p_value < 0.05),
                'avg_daily_volume': float(daily_counts['count'].mean()),
                'max_daily_volume': int(daily_counts['count'].max()),
                'min_daily_volume': int(daily_counts['count'].min())
            }
        
        # Hourly patterns
        hourly_counts = self.data.groupby('hour').size()
        volume_trends['hourly_patterns'] = {
            'peak_hours': hourly_counts.nlargest(3).index.tolist(),
            'low_hours': hourly_counts.nsmallest(3).index.tolist(),
            'hourly_distribution': hourly_counts.to_dict()
        }
        
        # Weekly patterns
        weekday_counts = self.data.groupby('weekday').size()
        volume_trends['weekly_patterns'] = {
            'busiest_days': weekday_counts.nlargest(3).index.tolist(),
            'quietest_days': weekday_counts.nsmallest(3).index.tolist(),
            'weekly_distribution': weekday_counts.to_dict()
        }
        
        return volume_trends
    
    def generate_trend_report(self) -> Dict[str, Any]:
        """Generate comprehensive trend analysis report."""
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'data_period': {
                'start_date': str(self.data['date'].min()) if 'date' in self.data.columns else None,
                'end_date': str(self.data['date'].max()) if 'date' in self.data.columns else None,
                'total_days': (self.data['date'].max() - self.data['date'].min()).days if 'date' in self.data.columns else None
            }
        }
        
        try:
            report['price_trends'] = self.price_trends()
        except Exception as e:
            self.logger.error(f"Error in price trends: {e}")
        
        try:
            report['volume_trends'] = self.volume_trends()
        except Exception as e:
            self.logger.error(f"Error in volume trends: {e}")
        
        return report