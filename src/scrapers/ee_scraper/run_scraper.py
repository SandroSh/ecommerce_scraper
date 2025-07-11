#!/usr/bin/env python3
"""
Standalone EE Scraper Runner

This module provides a standalone execution interface for the EE scraper.
It can be run directly from the ee_scraper directory and includes command-line
argument parsing, logging setup, and error handling.

The module handles:
- Command-line argument parsing
- Logging configuration
- Scraper initialization and execution
- Output file management
- Error handling and reporting
"""

import sys
import os
import argparse
import logging
from datetime import datetime
import shutil
from pathlib import Path

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

try:
    from src.scrapers.ee_scraper.ee_scraper import EEScraper
    from src.utils.logger import get_logger
    from src.utils.data_helpers import save_products_to_json
    from src.data.processors import DataProcessor
    from analyze_data import run_analysis
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def setup_logging():
    """
    Configure logging for the scraper with both file and console output.
    
    Sets up a logging configuration that writes to both a log file and
    the console. The log file is named 'ee_scraper.log' and includes
    timestamps, logger names, and log levels.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ee_scraper.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def get_next_incremented_folder(base_dir, prefix):
    """
    Find the next available incremented folder (e.g., processed1, processed2, ...).
    Returns the path to the new folder.
    """
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)
    i = 1
    while (base / f"{prefix}{i}").exists():
        i += 1
    new_folder = base / f"{prefix}{i}"
    new_folder.mkdir()
    return str(new_folder)

def delete_file(filepath):
    try:
        os.remove(filepath)
    except Exception as e:
        logging.warning(f"Could not delete file {filepath}: {e}")

def parse_arguments():
    """
    Parse command-line arguments for the EE scraper.
    
    Defines and parses command-line arguments including:
    - max_products: Maximum number of products to scrape
    - sleep: Delay between requests
    - output_dir: Directory for output files
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description='EE Mobile Phone Scraper')
    parser.add_argument('--max_products', type=int, default=0,
                        help='Maximum number of products to scrape (0 = all products, default: 0)')
    parser.add_argument('--sleep', type=float, default=1.0,
                        help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--output_dir', type=str, default='data_output/raw',
                        help='Directory to save output files (default: data_output/raw)')
    return parser.parse_args()

def main():
    """
    Main execution function for the EE scraper.
    
    This function orchestrates the entire scraping process:
    1. Parses command-line arguments
    2. Sets up logging
    3. Creates output directory
    4. Initializes and runs the scraper
    5. Saves results to output files
    6. Handles errors and provides status reporting
    
    The function includes comprehensive error handling and will exit
    with status code 1 if any critical errors occur.
    """
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("Starting EE Mobile Phone Scraper")
    logger.info(f"Max products: {args.max_products if args.max_products > 0 else 'All'}")
    logger.info(f"Sleep delay: {args.sleep} seconds")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info("=" * 50)

    try:
        # Step 1: Scrape and save raw data
        output_dir = os.path.abspath(args.output_dir)
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory created/verified: {output_dir}")
        scraper = EEScraper(max_products=args.max_products, sleep=args.sleep)
        products = scraper.run()
        if not products:
            logger.warning("No products were scraped")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_json_file = os.path.join(output_dir, f"ee_phones_{timestamp}.json")
        save_products_to_json(products, raw_json_file)
        logger.info(f"Successfully scraped {len(products)} products")
        logger.info(f"Raw results saved to: {raw_json_file}")

        # Step 2: Process raw data into new processedN folder
        processed_base = os.path.join(project_root, "data_output", "processed")
        processed_folder = get_next_incremented_folder(processed_base, "processed")
        logger.info(f"Processing raw data into: {processed_folder}")
        processor = DataProcessor()
        processing_report = processor.process_file(raw_json_file, processed_folder)
        logger.info(f"Processing report: {processing_report}")

        # Step 3: Delete raw data file
        delete_file(raw_json_file)
        logger.info(f"Deleted raw data file: {raw_json_file}")

        # Step 4: Analyze processed data and save reports in new reportN folder
        report_base = os.path.join(project_root, "data_output", "reports")
        report_folder = get_next_incremented_folder(report_base, "report")
        logger.info(f"Running analysis, reports will be saved in: {report_folder}")
        # Find processed JSON files in processed_folder
        processed_files = [str(f) for f in Path(processed_folder).glob("*.json")]
        if not processed_files:
            logger.warning(f"No processed JSON files found in {processed_folder}")
            return
        import pandas as pd
        from src.analysis.statistics import StatisticalAnalyzer
        from src.analysis.trends import TrendAnalyzer
        from src.analysis.reports import ReportGenerator
        from analyze_data import load_data
        data = load_data(processed_files)
        run_analysis(data, output_dir=report_folder)
        logger.info(f"Analysis and report generation complete. Reports saved in: {report_folder}")

    except Exception as e:
        logger.error(f"Error running scraper: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    logger.info("EE scraper finished successfully!")

if __name__ == "__main__":
    main() 