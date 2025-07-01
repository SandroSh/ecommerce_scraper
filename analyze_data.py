#!/usr/bin/env python3
"""
E-commerce Data Analysis Script
Analyzes processed data files and generates comprehensive reports.
"""

import sys
import os
import json
import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analysis.reports import ReportGenerator
from src.analysis.statistics import StatisticalAnalyzer
from src.analysis.trends import TrendAnalyzer


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('analysis.log')
        ]
    )


def find_processed_files(data_dir: str = "data_output/processed") -> List[str]:
    """Find processed JSON files in the data directory."""
    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    json_files = list(data_path.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {data_dir}")

    return [str(f) for f in json_files]


def load_data(file_paths: List[str]) -> pd.DataFrame:
    """Load and combine data from multiple JSON files."""
    all_data = []

    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                all_data.extend(data)
            else:
                all_data.append(data)

            logging.info(f"Loaded {len(data) if isinstance(data, list) else 1} records from {file_path}")

        except Exception as e:
            logging.error(f"Error loading {file_path}: {e}")
            continue

    if not all_data:
        raise ValueError("No data loaded from input files")

    df = pd.DataFrame(all_data)
    logging.info(f"Total records loaded: {len(df)}")
    return df


def run_analysis(data: pd.DataFrame, output_dir: str = "data_output/reports") -> Dict[str, Any]:
    """Run comprehensive analysis on the data."""
    logging.info("Starting comprehensive data analysis...")

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Initialize analyzers
    stats_analyzer = StatisticalAnalyzer(data)
    trend_analyzer = TrendAnalyzer(data)
    report_generator = ReportGenerator(data, output_dir)

    # Run analyses
    results = {}

    try:
        logging.info("Running statistical analysis...")
        results['statistical_analysis'] = stats_analyzer.generate_summary_report()

        logging.info("Running trend analysis...")
        results['trend_analysis'] = trend_analyzer.generate_trend_report()

        logging.info("Generating comprehensive report...")
        generated_files = report_generator.generate_complete_report()
        results['generated_files'] = generated_files

        logging.info("Analysis completed successfully!")
        return results

    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        raise


def print_summary(results: Dict[str, Any], data: pd.DataFrame):
    """Print analysis summary to console."""
    print("\n" + "=" * 60)
    print("E-COMMERCE DATA ANALYSIS SUMMARY")
    print("=" * 60)

    # Data overview
    print(f"\n📊 DATA OVERVIEW:")
    print(f"   • Total records: {len(data):,}")
    print(f"   • Columns: {', '.join(data.columns.tolist())}")

    # Statistical insights
    if 'statistical_analysis' in results:
        stats = results['statistical_analysis']
        if 'descriptive_statistics' in stats:
            desc_stats = stats['descriptive_statistics']

            print(f"\n💰 PRICE STATISTICS:")
            if 'price_statistics' in desc_stats:
                price_stats = desc_stats['price_statistics']
                print(f"   • Average price: {price_stats.get('mean', 0):.0f} GEL")
                print(f"   • Price range: {price_stats.get('min', 0):.0f} - {price_stats.get('max', 0):.0f} GEL")
                print(f"   • Median price: {price_stats.get('median', 0):.0f} GEL")

            print(f"\n🏷️  CATEGORIES & BRANDS:")
            if 'overview' in desc_stats:
                overview = desc_stats['overview']
                if 'categories' in overview:
                    print(f"   • Categories: {len(overview['categories'])}")
                    top_cat = max(overview['categories'].items(), key=lambda x: x[1])
                    print(f"   • Top category: {top_cat[0]} ({top_cat[1]} products)")

                if 'brands' in overview:
                    print(f"   • Brands: {len(overview['brands'])}")
                    if overview['brands']:
                        top_brand = max(overview['brands'].items(), key=lambda x: x[1])
                        print(f"   • Top brand: {top_brand[0]} ({top_brand[1]} products)")

    # Trend insights
    if 'trend_analysis' in results:
        trends = results['trend_analysis']
        print(f"\n📈 TREND ANALYSIS:")

        if 'price_trends' in trends and 'daily_trends' in trends['price_trends']:
            daily_trends = trends['price_trends']['daily_trends']
            direction = daily_trends.get('trend_direction', 'unknown')
            significant = daily_trends.get('is_significant', False)
            print(f"   • Price trend: {direction.upper()}")
            print(f"   • Trend significance: {'Yes' if significant else 'No'}")

        if 'volume_trends' in trends and 'daily_volume' in trends['volume_trends']:
            vol_trends = trends['volume_trends']['daily_volume']
            avg_daily = vol_trends.get('avg_daily_volume', 0)
            print(f"   • Avg daily records: {avg_daily:.0f}")

    # Generated files
    if 'generated_files' in results:
        print(f"\n📁 GENERATED FILES:")
        for file_type, file_path in results['generated_files'].items():
            print(f"   • {file_type}: {file_path}")

    print("\n" + "=" * 60)


def main():
    """Main function."""
    setup_logging()

    try:
        # Find processed files
        logging.info("Looking for processed data files...")
        processed_files = find_processed_files()
        print(f"Found {len(processed_files)} processed file(s):")
        for f in processed_files:
            print(f"  • {f}")

        # Load data
        print(f"\nLoading data...")
        data = load_data(processed_files)

        # Run analysis
        print(f"Running comprehensive analysis...")
        results = run_analysis(data)

        # Print summary
        print_summary(results, data)

        print(f"\nAnalysis completed successfully!")

    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        print(f"\nAnalysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()