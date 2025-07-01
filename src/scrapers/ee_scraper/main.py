"""
EE Scraper Main Module

This module provides the main entry point for the EE scraper application.
It handles command-line argument parsing and initializes the scraper with
the specified configuration parameters.

The module is designed to be run as a standalone script and provides
a simple interface for executing the EE scraper with custom parameters.
"""

import argparse
import logging
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from src.scrapers.ee_scraper.ee_scraper import EEScraper
from src.utils.logger import get_logger

def parse_args():
    """
    Parse command-line arguments for the EE scraper.
    
    Defines the available command-line options including:
    - max_products: Maximum number of products to scrape (0 = all)
    - sleep: Delay between requests in seconds
    - output_dir: Directory to save output files
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description='EE Mobile Scraper')
    parser.add_argument('--max_products', type=int, default=0,
                        help='Maximum number of products to scrape (0 = all)')
    parser.add_argument('--sleep', type=float, default=1.0,
                        help='Delay between requests in seconds')
    parser.add_argument('--output_dir', type=str, default='data_output/raw',
                        help='Directory to save output files (default: data_output/raw)')
    return parser.parse_args()

def main():
    """
    Main execution function for the EE scraper.
    
    This function serves as the primary entry point for the EE scraper
    application. It parses command-line arguments, initializes logging,
    creates the scraper instance, and executes the scraping process.
    
    The function provides basic error handling and status reporting
    through the logger system.
    """
    args = parse_args()
    logger = get_logger("ee_scraper_main")
    logger.info("Launching EE scraper...")

    scraper = EEScraper(max_products=args.max_products, sleep=args.sleep)
    scraper.run()

    logger.info("EE scraper finished successfully.")

if __name__ == "__main__":
    main()
