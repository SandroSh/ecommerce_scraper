"""
Automated report generation module for e-commerce data analysis.
Creates comprehensive reports with insights, visualizations, and summaries.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import json
from pathlib import Path

# Optional visualization imports
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False
    logging.warning("Matplotlib/Seaborn not available. Visualizations will be disabled.")

from .statistics import StatisticalAnalyzer, ComparativeAnalyzer
from .trends import TrendAnalyzer

class ReportGenerator:
    """Generate comprehensive automated reports for e-commerce data."""
    
    def __init__(self, data: pd.DataFrame, output_dir: str = "data_output/reports"):
        self.data = data.copy()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Set matplotlib style if available
        if HAS_VISUALIZATION:
            plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
            sns.set_palette("husl")
    
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary with key insights."""
        analyzer = StatisticalAnalyzer(self.data)
        stats = analyzer.descriptive_statistics()
        
        summary = {
            'report_date': datetime.now().isoformat(),
            'data_overview': {
                'total_products': len(self.data),
                'date_range': stats.get('overview', {}).get('date_range', {}),
                'categories_covered': len(stats.get('overview', {}).get('categories', {})),
                'brands_covered': len(stats.get('overview', {}).get('brands', {}))
            }
        }
        
        # Key insights
        insights = []
        
        # Price insights
        if 'price_statistics' in stats:
            price_stats = stats['price_statistics']
            avg_price = price_stats.get('mean', 0)
            insights.append(f"Average product price is {avg_price:.0f} GEL")
            
            if price_stats.get('skewness', 0) > 1:
                insights.append("Price distribution is heavily skewed towards lower prices")
            
            # Category price insights
            if 'price_by_category' in stats:
                cat_prices = stats['price_by_category']
                if len(cat_prices) > 1:  # Only compare if multiple categories
                    highest_cat = max(cat_prices.items(), key=lambda x: x[1]['mean'])
                    lowest_cat = min(cat_prices.items(), key=lambda x: x[1]['mean'])
                    insights.append(f"{highest_cat[0]} has the highest average prices ({highest_cat[1]['mean']:.0f} GEL)")
                    insights.append(f"{lowest_cat[0]} has the lowest average prices ({lowest_cat[1]['mean']:.0f} GEL)")
                elif len(cat_prices) == 1:  # Single category
                    category, prices = list(cat_prices.items())[0]
                    insights.append(f"All products are in {category} category with average price {prices['mean']:.0f} GEL")
        
        # Brand insights
        if 'overview' in stats and 'brands' in stats['overview']:
            brands = stats['overview']['brands']
            if brands:
                top_brand = max(brands.items(), key=lambda x: x[1])
                market_share = top_brand[1] / len(self.data) * 100
                insights.append(f"{top_brand[0]} dominates with {market_share:.1f}% market share")
        
        summary['key_insights'] = insights
        return summary
    
    def create_visualizations(self) -> Dict[str, str]:
        """Create and save visualization charts."""
        viz_files = {}
        
        if not HAS_VISUALIZATION:
            self.logger.warning("Visualization libraries not available, skipping chart generation")
            return viz_files
        
        # Set up the plotting style
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
        # 1. Price distribution
        if 'price' in self.data.columns:
            plt.figure(figsize=(12, 6))
            
            plt.subplot(1, 2, 1)
            self.data['price'].hist(bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            plt.title('Price Distribution')
            plt.xlabel('Price (GEL)')
            plt.ylabel('Frequency')
            
            plt.subplot(1, 2, 2)
            self.data.boxplot(column='price', ax=plt.gca())
            plt.title('Price Box Plot')
            plt.ylabel('Price (GEL)')
            
            plt.tight_layout()
            price_dist_file = self.output_dir / 'price_distribution.png'
            plt.savefig(price_dist_file, dpi=300, bbox_inches='tight')
            plt.close()
            viz_files['price_distribution'] = str(price_dist_file)
        
        # 2. Category analysis
        if 'category' in self.data.columns:
            plt.figure(figsize=(15, 10))
            
            # Category counts
            plt.subplot(2, 2, 1)
            category_counts = self.data['category'].value_counts()
            category_counts.plot(kind='bar', color='lightcoral')
            plt.title('Products by Category')
            plt.xlabel('Category')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Category pie chart
            plt.subplot(2, 2, 2)
            category_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90)
            plt.title('Category Distribution')
            plt.ylabel('')
            
            # Price by category
            if 'price' in self.data.columns:
                plt.subplot(2, 2, 3)
                self.data.boxplot(column='price', by='category', ax=plt.gca())
                plt.title('Price Distribution by Category')
                plt.xlabel('Category')
                plt.ylabel('Price (GEL)')
                plt.xticks(rotation=45)
                
                plt.subplot(2, 2, 4)
                category_avg_prices = self.data.groupby('category')['price'].mean().sort_values(ascending=False)
                category_avg_prices.plot(kind='bar', color='lightgreen')
                plt.title('Average Price by Category')
                plt.xlabel('Category')
                plt.ylabel('Average Price (GEL)')
                plt.xticks(rotation=45)
            
            plt.tight_layout()
            category_file = self.output_dir / 'category_analysis.png'
            plt.savefig(category_file, dpi=300, bbox_inches='tight')
            plt.close()
            viz_files['category_analysis'] = str(category_file)
        
        # 3. Brand analysis
        if 'brand' in self.data.columns:
            plt.figure(figsize=(15, 6))
            
            # Top brands by count
            plt.subplot(1, 2, 1)
            top_brands = self.data['brand'].value_counts().head(10)
            top_brands.plot(kind='bar', color='gold')
            plt.title('Top 10 Brands by Product Count')
            plt.xlabel('Brand')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Brand price comparison
            if 'price' in self.data.columns:
                plt.subplot(1, 2, 2)
                brand_avg_prices = self.data.groupby('brand')['price'].mean().sort_values(ascending=False).head(10)
                brand_avg_prices.plot(kind='bar', color='orange')
                plt.title('Top 10 Brands by Average Price')
                plt.xlabel('Brand')
                plt.ylabel('Average Price (GEL)')
                plt.xticks(rotation=45)
            
            plt.tight_layout()
            brand_file = self.output_dir / 'brand_analysis.png'
            plt.savefig(brand_file, dpi=300, bbox_inches='tight')
            plt.close()
            viz_files['brand_analysis'] = str(brand_file)
        
        # 4. Time series analysis
        if 'createdat' in self.data.columns:
            self.data['createdat'] = pd.to_datetime(self.data['createdat'], errors='coerce')
            time_data = self.data.dropna(subset=['createdat'])
            
            if len(time_data) > 0:
                plt.figure(figsize=(15, 8))
                
                # Daily volume
                plt.subplot(2, 2, 1)
                daily_counts = time_data.groupby(time_data['createdat'].dt.date).size()
                daily_counts.plot(kind='line', marker='o', color='blue')
                plt.title('Daily Scraping Volume')
                plt.xlabel('Date')
                plt.ylabel('Products Scraped')
                plt.xticks(rotation=45)
                
                # Hourly patterns
                plt.subplot(2, 2, 2)
                hourly_counts = time_data.groupby(time_data['createdat'].dt.hour).size()
                hourly_counts.plot(kind='bar', color='purple')
                plt.title('Hourly Scraping Patterns')
                plt.xlabel('Hour of Day')
                plt.ylabel('Products Scraped')
                
                # Daily price trends
                if 'price' in time_data.columns:
                    plt.subplot(2, 2, 3)
                    daily_prices = time_data.groupby(time_data['createdat'].dt.date)['price'].mean()
                    daily_prices.plot(kind='line', marker='o', color='red')
                    plt.title('Daily Average Price Trends')
                    plt.xlabel('Date')
                    plt.ylabel('Average Price (GEL)')
                    plt.xticks(rotation=45)
                
                # Weekday patterns
                plt.subplot(2, 2, 4)
                weekday_counts = time_data.groupby(time_data['createdat'].dt.day_name()).size()
                # Reorder to start with Monday
                weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                weekday_counts = weekday_counts.reindex([day for day in weekday_order if day in weekday_counts.index])
                weekday_counts.plot(kind='bar', color='teal')
                plt.title('Weekday Scraping Patterns')
                plt.xlabel('Day of Week')
                plt.ylabel('Products Scraped')
                plt.xticks(rotation=45)
                
                plt.tight_layout()
                time_file = self.output_dir / 'time_analysis.png'
                plt.savefig(time_file, dpi=300, bbox_inches='tight')
                plt.close()
                viz_files['time_analysis'] = str(time_file)
        
        return viz_files
    
    def generate_detailed_report(self) -> Dict[str, Any]:
        """Generate detailed analysis report."""
        # Initialize analyzers
        stats_analyzer = StatisticalAnalyzer(self.data)
        trend_analyzer = TrendAnalyzer(self.data)
        
        # Generate comprehensive analysis
        detailed_report = {
            'metadata': {
                'report_timestamp': datetime.now().isoformat(),
                'data_summary': {
                    'total_records': len(self.data),
                    'columns': list(self.data.columns),
                    'memory_usage': f"{self.data.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
                }
            },
            'executive_summary': self.generate_executive_summary(),
            'statistical_analysis': stats_analyzer.generate_summary_report(),
            'trend_analysis': trend_analyzer.generate_trend_report()
        }
        
        # Add comparative analysis if multiple sources/categories exist
        if 'source' in self.data.columns and len(self.data['source'].unique()) > 1:
            comp_analyzer = ComparativeAnalyzer(self.data)
            detailed_report['comparative_analysis'] = {
                'source_comparison': comp_analyzer.compare_sources()
            }
        
        return detailed_report
    
    def export_report(self, report_data: Dict[str, Any], format: str = 'json') -> str:
        """Export report in specified format."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = f"ecommerce_analysis_report_{timestamp}.json"
            filepath = self.output_dir / filename
            
            # Custom JSON encoder for dates and numpy types
            def json_serializer(obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                elif hasattr(obj, 'item'):
                    return obj.item()
                elif hasattr(obj, 'tolist'):
                    return obj.tolist()
                return str(obj)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=json_serializer)
                
        elif format == 'html':
            filename = f"ecommerce_analysis_report_{timestamp}.html"
            filepath = self.output_dir / filename
            
            html_content = self._generate_html_report(report_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        self.logger.info(f"Report exported to: {filepath}")
        return str(filepath)
    
    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML formatted report."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>E-commerce Data Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { background-color: #f4f4f4; padding: 20px; border-radius: 5px; }
                .section { margin: 20px 0; padding: 15px; border-left: 4px solid #007ACC; }
                .insight { background-color: #e8f4f8; padding: 10px; margin: 10px 0; border-radius: 3px; }
                .metric { display: inline-block; margin: 10px; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }
                table { border-collapse: collapse; width: 100%; margin: 10px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .chart { text-align: center; margin: 20px 0; }
            </style>
        </head>
        <body>
        """
        
        # Header
        html += f"""
        <div class="header">
            <h1>E-commerce Data Analysis Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Total Records Analyzed: {len(self.data):,}</p>
        </div>
        """
        
        # Executive Summary
        if 'executive_summary' in report_data:
            summary = report_data['executive_summary']
            html += """
            <div class="section">
                <h2>Executive Summary</h2>
            """
            
            if 'key_insights' in summary:
                html += "<h3>Key Insights:</h3>"
                for insight in summary['key_insights']:
                    html += f'<div class="insight">" {insight}</div>'
            
            html += "</div>"
        
        # Statistical Overview
        if 'statistical_analysis' in report_data:
            stats = report_data['statistical_analysis']
            html += """
            <div class="section">
                <h2>Statistical Overview</h2>
            """
            
            if 'descriptive_statistics' in stats:
                desc_stats = stats['descriptive_statistics']
                
                # Price statistics
                if 'price_statistics' in desc_stats:
                    price_stats = desc_stats['price_statistics']
                    html += """
                    <h3>Price Statistics</h3>
                    <div style="display: flex; flex-wrap: wrap;">
                    """
                    html += f'<div class="metric"><strong>Average:</strong><br>{price_stats.get("mean", 0):.0f} GEL</div>'
                    html += f'<div class="metric"><strong>Median:</strong><br>{price_stats.get("median", 0):.0f} GEL</div>'
                    html += f'<div class="metric"><strong>Min:</strong><br>{price_stats.get("min", 0):.0f} GEL</div>'
                    html += f'<div class="metric"><strong>Max:</strong><br>{price_stats.get("max", 0):.0f} GEL</div>'
                    html += "</div>"
                
                # Category breakdown
                if 'overview' in desc_stats and 'categories' in desc_stats['overview']:
                    categories = desc_stats['overview']['categories']
                    html += """
                    <h3>Category Breakdown</h3>
                    <table>
                        <tr><th>Category</th><th>Count</th><th>Percentage</th></tr>
                    """
                    total = sum(categories.values())
                    for cat, count in categories.items():
                        percentage = count / total * 100
                        html += f"<tr><td>{cat}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>"
                    html += "</table>"
            
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def generate_complete_report(self) -> Dict[str, str]:
        """Generate complete report with all components."""
        self.logger.info("Generating comprehensive analysis report...")
        
        # Generate detailed analysis
        report_data = self.generate_detailed_report()
        
        # Create visualizations
        viz_files = self.create_visualizations()
        
        # Export reports in multiple formats
        exported_files = {}
        
        # JSON report
        json_file = self.export_report(report_data, format='json')
        exported_files['json_report'] = json_file
        
        # HTML report
        html_file = self.export_report(report_data, format='html')
        exported_files['html_report'] = html_file
        
        # Add visualization files
        exported_files.update(viz_files)
        
        # Create summary file
        summary_file = self.output_dir / f"report_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("E-COMMERCE DATA ANALYSIS REPORT SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Records: {len(self.data):,}\n")
            f.write(f"Date Range: {report_data.get('statistical_analysis', {}).get('descriptive_statistics', {}).get('overview', {}).get('date_range', {})}\n\n")
            
            # Key insights
            insights = report_data.get('executive_summary', {}).get('key_insights', [])
            if insights:
                f.write("KEY INSIGHTS:\n")
                for i, insight in enumerate(insights, 1):
                    f.write(f"{i}. {insight}\n")
            
            f.write(f"\nFiles Generated:\n")
            for file_type, file_path in exported_files.items():
                f.write(f"- {file_type}: {file_path}\n")
        
        exported_files['summary'] = str(summary_file)
        
        self.logger.info(f"Complete report generated. Files: {list(exported_files.keys())}")
        return exported_files


def create_analysis_pipeline(input_files: List[str], output_dir: str = None) -> Dict[str, Any]:
    """Complete analysis pipeline for processing multiple data files."""
    if output_dir is None:
        output_dir = "data_output/reports"
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting analysis pipeline for {len(input_files)} files")
    
    # Load and combine all data
    all_data = []
    for file_path in input_files:
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
    
    if not all_data:
        return {'error': 'No data loaded from input files'}
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Generate comprehensive report
    report_generator = ReportGenerator(df, output_dir)
    results = report_generator.generate_complete_report()
    
    pipeline_results = {
        'input_files': input_files,
        'total_records_processed': len(df),
        'output_directory': output_dir,
        'generated_files': results,
        'pipeline_timestamp': datetime.now().isoformat()
    }
    
    return pipeline_results