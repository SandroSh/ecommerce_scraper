"""
Statistical analysis module for e-commerce data.
Provides descriptive statistics, distributions, and comparative analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Optional imports
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logging.warning("SciPy not available. Some statistical tests will be disabled.")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False

class StatisticalAnalyzer:
    """Comprehensive statistical analysis for e-commerce data."""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.logger = logging.getLogger(__name__)
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare data for analysis."""
        if 'createdat' in self.data.columns:
            self.data['createdat'] = pd.to_datetime(self.data['createdat'], errors='coerce')
        
        if 'price' in self.data.columns:
            self.data['price'] = pd.to_numeric(self.data['price'], errors='coerce')
    
    def descriptive_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive descriptive statistics."""
        stats_report = {
            'overview': {
                'total_records': len(self.data),
                'date_range': self._get_date_range(),
                'categories': self.data['category'].value_counts().to_dict() if 'category' in self.data.columns else {},
                'sources': self.data['source'].value_counts().to_dict() if 'source' in self.data.columns else {},
                'brands': self.data['brand'].value_counts().to_dict() if 'brand' in self.data.columns else {}
            }
        }
        
        # Price statistics
        if 'price' in self.data.columns:
            price_data = self.data['price'].dropna()
            stats_report['price_statistics'] = {
                'count': len(price_data),
                'mean': float(price_data.mean()),
                'median': float(price_data.median()),
                'std': float(price_data.std()),
                'min': float(price_data.min()),
                'max': float(price_data.max()),
                'q25': float(price_data.quantile(0.25)),
                'q75': float(price_data.quantile(0.75)),
                'iqr': float(price_data.quantile(0.75) - price_data.quantile(0.25)),
                'skewness': float(stats.skew(price_data)) if HAS_SCIPY else None,
                'kurtosis': float(stats.kurtosis(price_data)) if HAS_SCIPY else None
            }
            
            # Price by category
            if 'category' in self.data.columns:
                stats_report['price_by_category'] = {}
                for category in self.data['category'].unique():
                    cat_prices = self.data[self.data['category'] == category]['price'].dropna()
                    if len(cat_prices) > 0:
                        stats_report['price_by_category'][category] = {
                            'count': len(cat_prices),
                            'mean': float(cat_prices.mean()),
                            'median': float(cat_prices.median()),
                            'std': float(cat_prices.std()),
                            'min': float(cat_prices.min()),
                            'max': float(cat_prices.max())
                        }
        
        # Text field statistics
        text_fields = ['name', 'description', 'brand']
        stats_report['text_statistics'] = {}
        
        for field in text_fields:
            if field in self.data.columns:
                text_data = self.data[field].astype(str)
                stats_report['text_statistics'][field] = {
                    'avg_length': float(text_data.str.len().mean()),
                    'min_length': int(text_data.str.len().min()),
                    'max_length': int(text_data.str.len().max()),
                    'unique_count': int(text_data.nunique()),
                    'empty_count': int((text_data == '').sum())
                }
        
        return stats_report
    
    def _get_date_range(self) -> Dict[str, str]:
        """Get date range of the data."""
        if 'createdat' not in self.data.columns:
            return {}
        
        dates = pd.to_datetime(self.data['createdat'], errors='coerce').dropna()
        if len(dates) == 0:
            return {}
        
        return {
            'start_date': dates.min().isoformat(),
            'end_date': dates.max().isoformat(),
            'span_days': (dates.max() - dates.min()).days
        }
    
    def price_distribution_analysis(self) -> Dict[str, Any]:
        """Analyze price distributions and identify patterns."""
        if 'price' not in self.data.columns:
            return {'error': 'No price data available'}
        
        price_data = self.data['price'].dropna()
        
        analysis = {
            'distribution_tests': {},
            'outliers': {},
            'price_segments': {}
        }
        
        # Test for normal distribution
        try:
            shapiro_stat, shapiro_p = stats.shapiro(price_data.sample(min(5000, len(price_data))))
            analysis['distribution_tests']['shapiro_wilk'] = {
                'statistic': float(shapiro_stat),
                'p_value': float(shapiro_p),
                'is_normal': bool(shapiro_p > 0.05)
            }
        except:
            pass
        
        # Kolmogorov-Smirnov test for normal distribution
        try:
            ks_stat, ks_p = stats.kstest(price_data, 'norm')
            analysis['distribution_tests']['kolmogorov_smirnov'] = {
                'statistic': float(ks_stat),
                'p_value': float(ks_p),
                'is_normal': bool(ks_p > 0.05)
            }
        except:
            pass
        
        # Outlier detection using IQR method
        Q1 = price_data.quantile(0.25)
        Q3 = price_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = price_data[(price_data < lower_bound) | (price_data > upper_bound)]
        analysis['outliers'] = {
            'count': len(outliers),
            'percentage': len(outliers) / len(price_data) * 100,
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'outlier_values': outliers.tolist()
        }
        
        # Price segmentation
        analysis['price_segments'] = {
            'budget': len(price_data[price_data <= price_data.quantile(0.33)]),
            'mid_range': len(price_data[(price_data > price_data.quantile(0.33)) & (price_data <= price_data.quantile(0.67))]),
            'premium': len(price_data[price_data > price_data.quantile(0.67)])
        }
        
        return analysis
    
    def brand_analysis(self) -> Dict[str, Any]:
        """Analyze brand distribution and characteristics."""
        if 'brand' not in self.data.columns:
            return {'error': 'No brand data available'}
        
        brand_analysis = {}
        
        # Brand market share
        brand_counts = self.data['brand'].value_counts()
        total_products = len(self.data)
        
        brand_analysis['market_share'] = {
            brand: {
                'count': int(count),
                'percentage': float(count / total_products * 100)
            }
            for brand, count in brand_counts.head(10).items()
        }
        
        # Brand price analysis
        if 'price' in self.data.columns:
            brand_price_stats = self.data.groupby('brand')['price'].agg([
                'count', 'mean', 'median', 'std', 'min', 'max'
            ]).round(2)
            
            brand_analysis['price_by_brand'] = brand_price_stats.to_dict('index')
            
            # Find premium vs budget brands
            brand_avg_prices = self.data.groupby('brand')['price'].mean()
            overall_median = self.data['price'].median()
            
            brand_analysis['brand_positioning'] = {
                'premium_brands': brand_avg_prices[brand_avg_prices > overall_median * 1.5].index.tolist(),
                'budget_brands': brand_avg_prices[brand_avg_prices < overall_median * 0.7].index.tolist()
            }
        
        return brand_analysis
    
    def category_analysis(self) -> Dict[str, Any]:
        """Analyze product categories and their characteristics."""
        if 'category' not in self.data.columns:
            return {'error': 'No category data available'}
        
        category_analysis = {}
        
        # Category distribution
        category_counts = self.data['category'].value_counts()
        total_products = len(self.data)
        
        category_analysis['distribution'] = {
            category: {
                'count': int(count),
                'percentage': float(count / total_products * 100)
            }
            for category, count in category_counts.items()
        }
        
        # Category price analysis
        if 'price' in self.data.columns:
            cat_price_stats = self.data.groupby('category')['price'].agg([
                'count', 'mean', 'median', 'std', 'min', 'max'
            ]).round(2)
            
            category_analysis['price_statistics'] = cat_price_stats.to_dict('index')
            
            # Price comparison between categories
            try:
                categories = self.data['category'].unique()
                if len(categories) > 1:
                    price_comparison = {}
                    for i, cat1 in enumerate(categories):
                        for cat2 in categories[i+1:]:
                            cat1_prices = self.data[self.data['category'] == cat1]['price'].dropna()
                            cat2_prices = self.data[self.data['category'] == cat2]['price'].dropna()
                            
                            if len(cat1_prices) > 0 and len(cat2_prices) > 0:
                                t_stat, p_value = stats.ttest_ind(cat1_prices, cat2_prices)
                                price_comparison[f"{cat1}_vs_{cat2}"] = {
                                    't_statistic': float(t_stat),
                                    'p_value': float(p_value),
                                    'significant_difference': bool(p_value < 0.05)
                                }
                    
                    category_analysis['price_comparisons'] = price_comparison
            except:
                pass
        
        return category_analysis
    
    def correlation_analysis(self) -> Dict[str, Any]:
        """Analyze correlations between numerical variables."""
        numeric_columns = self.data.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_columns) < 2:
            return {'error': 'Insufficient numerical data for correlation analysis'}
        
        correlation_matrix = self.data[numeric_columns].corr()
        
        # Find strong correlations (> 0.7 or < -0.7)
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        'variable1': correlation_matrix.columns[i],
                        'variable2': correlation_matrix.columns[j],
                        'correlation': float(corr_value)
                    })
        
        return {
            'correlation_matrix': correlation_matrix.round(3).to_dict(),
            'strong_correlations': strong_correlations,
            'numerical_variables': numeric_columns
        }
    
    def time_series_analysis(self) -> Dict[str, Any]:
        """Analyze time-based patterns in the data."""
        if 'createdat' not in self.data.columns:
            return {'error': 'No timestamp data available'}
        
        time_data = self.data.copy()
        time_data['createdat'] = pd.to_datetime(time_data['createdat'], errors='coerce')
        time_data = time_data.dropna(subset=['createdat'])
        
        if len(time_data) == 0:
            return {'error': 'No valid timestamp data'}
        
        time_analysis = {}
        
        # Daily patterns
        time_data['date'] = time_data['createdat'].dt.date
        time_data['hour'] = time_data['createdat'].dt.hour
        time_data['weekday'] = time_data['createdat'].dt.day_name()
        
        # Records per day
        daily_counts = time_data.groupby('date').size()
        time_analysis['daily_patterns'] = {
            'records_per_day': {str(k): v for k, v in daily_counts.to_dict().items()},
            'avg_daily_records': float(daily_counts.mean()),
            'max_daily_records': int(daily_counts.max()),
            'min_daily_records': int(daily_counts.min())
        }
        
        # Hourly patterns
        hourly_counts = time_data.groupby('hour').size()
        time_analysis['hourly_patterns'] = {
            'records_by_hour': hourly_counts.to_dict(),
            'peak_hour': int(hourly_counts.idxmax()),
            'lowest_hour': int(hourly_counts.idxmin())
        }
        
        # Weekly patterns
        weekday_counts = time_data.groupby('weekday').size()
        time_analysis['weekly_patterns'] = {
            'records_by_weekday': weekday_counts.to_dict(),
            'busiest_day': weekday_counts.idxmax(),
            'quietest_day': weekday_counts.idxmin()
        }
        
        # Price trends over time (if available)
        if 'price' in time_data.columns:
            daily_price_stats = time_data.groupby('date')['price'].agg(['mean', 'median', 'count'])
            time_analysis['price_trends'] = {
                'daily_avg_prices': {str(k): v for k, v in daily_price_stats['mean'].to_dict().items()},
                'price_volatility': float(daily_price_stats['mean'].std()),
                'trend_direction': self._calculate_trend_direction(daily_price_stats['mean'])
            }
        
        return time_analysis
    
    def _calculate_trend_direction(self, series: pd.Series) -> str:
        """Calculate overall trend direction."""
        if len(series) < 2:
            return 'insufficient_data'
        
        # Simple linear regression to determine trend
        x = np.arange(len(series))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, series.values)
        
        if p_value < 0.05:  # Significant trend
            if slope > 0:
                return 'increasing'
            else:
                return 'decreasing'
        else:
            return 'stable'
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a comprehensive summary report."""
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'data_overview': {
                'total_records': len(self.data),
                'columns': list(self.data.columns),
                'data_types': self.data.dtypes.astype(str).to_dict()
            }
        }
        
        # Add all analysis components
        try:
            report['descriptive_statistics'] = self.descriptive_statistics()
        except Exception as e:
            self.logger.error(f"Error in descriptive statistics: {e}")
        
        try:
            report['price_analysis'] = self.price_distribution_analysis()
        except Exception as e:
            self.logger.error(f"Error in price analysis: {e}")
        
        try:
            report['brand_analysis'] = self.brand_analysis()
        except Exception as e:
            self.logger.error(f"Error in brand analysis: {e}")
        
        try:
            report['category_analysis'] = self.category_analysis()
        except Exception as e:
            self.logger.error(f"Error in category analysis: {e}")
        
        try:
            report['correlation_analysis'] = self.correlation_analysis()
        except Exception as e:
            self.logger.error(f"Error in correlation analysis: {e}")
        
        try:
            report['time_analysis'] = self.time_series_analysis()
        except Exception as e:
            self.logger.error(f"Error in time series analysis: {e}")
        
        return report


class ComparativeAnalyzer:
    """Compare data across different sources, time periods, or categories."""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.logger = logging.getLogger(__name__)
    
    def compare_sources(self) -> Dict[str, Any]:
        """Compare metrics across different data sources."""
        if 'source' not in self.data.columns:
            return {'error': 'No source information available'}
        
        comparison = {}
        sources = self.data['source'].unique()
        
        for source in sources:
            source_data = self.data[self.data['source'] == source]
            analyzer = StatisticalAnalyzer(source_data)
            
            comparison[source] = {
                'record_count': len(source_data),
                'statistics': analyzer.descriptive_statistics()
            }
        
        return comparison
    
    def compare_time_periods(self, period: str = 'daily') -> Dict[str, Any]:
        """Compare metrics across different time periods."""
        if 'createdat' not in self.data.columns:
            return {'error': 'No timestamp data available'}
        
        time_data = self.data.copy()
        time_data['createdat'] = pd.to_datetime(time_data['createdat'], errors='coerce')
        time_data = time_data.dropna(subset=['createdat'])
        
        if period == 'daily':
            time_data['period'] = time_data['createdat'].dt.date
        elif period == 'hourly':
            time_data['period'] = time_data['createdat'].dt.floor('H')
        elif period == 'weekly':
            time_data['period'] = time_data['createdat'].dt.to_period('W')
        else:
            return {'error': f'Unsupported period: {period}'}
        
        comparison = {}
        for period_value in time_data['period'].unique():
            period_data = time_data[time_data['period'] == period_value]
            
            comparison[str(period_value)] = {
                'record_count': len(period_data),
                'avg_price': float(period_data['price'].mean()) if 'price' in period_data.columns else None,
                'categories': period_data['category'].value_counts().to_dict() if 'category' in period_data.columns else {}
            }
        
        return comparison