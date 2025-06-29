#!/usr/bin/env python3
"""
Standalone EE Scraper Runner
This file can be run directly from the ee_scraper directory
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

try:
    from src.scrapers.ee_scraper.ee_scraper import EEScraper
    from src.utils.logger import get_logger
    from src.utils.data_helpers import save_products_to_json
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def setup_logging():
    """Setup basic logging for the scraper"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ee_scraper.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='EE Mobile Phone Scraper')
    parser.add_argument('--max_products', type=int, default=0,
                        help='Maximum number of products to scrape (0 = all products, default: 0)')
    parser.add_argument('--sleep', type=float, default=1.0,
                        help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--output_dir', type=str, default='data_output/raw',
                        help='Directory to save output files (default: data_output/raw)')
    return parser.parse_args()

def main():
    """Main function to run the EE scraper"""
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
        # Create output directory if it doesn't exist - use absolute path
        output_dir = os.path.abspath(args.output_dir)
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory created/verified: {output_dir}")
        
        # Initialize and run scraper
        scraper = EEScraper(max_products=args.max_products, sleep=args.sleep)
        products = scraper.run()
        
        if products:
            # Save to output directory with absolute paths (JSON only)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_file = os.path.join(output_dir, f"ee_phones_{timestamp}.json")
            
            # Save file directly to the output directory
            save_products_to_json(products, json_file)
            
            logger.info(f"Successfully scraped {len(products)} products")
            logger.info(f"Results saved to: {json_file}")
        else:
            logger.warning("No products were scraped")
            
    except Exception as e:
        logger.error(f"Error running scraper: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    logger.info("EE scraper finished successfully!")

if __name__ == "__main__":
    main() 