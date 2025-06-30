"""
E-commerce Scraper Main Entry Point

This module serves as the main entry point for the ecommerce scraper application.
It provides a unified interface for running different scrapers (Scrapy-based and
BeautifulSoup-based) with configurable parameters and comprehensive logging.

The module supports multiple scraping sources:
- Zoomer (Scrapy-based spider)
- EE (BeautifulSoup-based scraper)

Features:
- Command-line argument parsing
- Configurable logging
- Multiple scraper support
- Category-based scraping
- Product limit controls
- Model version selection
"""

import argparse
import os
import sys
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def configure_logging():
    """
    Configure logging for the main application.
    
    Sets up logging with both file and console output, using a consistent
    format that includes timestamps, logger names, and log levels. The
    log file is named 'scraper.log'.
    
    The logging configuration applies to the entire application and ensures
    consistent logging across all components.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """
    Main execution function for the ecommerce scraper application.
    
    This function orchestrates the entire scraping process:
    1. Configures logging
    2. Parses command-line arguments
    3. Determines the appropriate scraper to use
    4. Configures scraper settings
    5. Executes the scraping process
    6. Provides status reporting
    
    The function supports two main scraping sources:
    - Zoomer: Uses Scrapy framework with configurable spider settings
    - EE: Uses BeautifulSoup with custom scraper implementation
    
    Command-line arguments allow customization of:
    - Scraping source (zoomer/ee)
    - Product category (phones/fridges/laptops/tvs)
    - Maximum number of products
    - Model version for data processing
    """
    configure_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='Run E-commerce product scraper')
    parser.add_argument('--source', type=str, default='zoomer',
                        choices=['zoomer', 'ee'],
                        help='Scraping source (zoomer = scrapy, ee = beautifulsoup)')
    parser.add_argument('--category', type=str, default='phones',
                        choices=['phones', 'fridges', 'laptops', 'tvs'],
                        help='Product category to scrape')
    parser.add_argument('--max_products', type=int, default=10,
                        help='Maximum number of products to scrape')
    parser.add_argument('--model_version', type=str, default='v1',
                        choices=['v1', 'v2', 'v3'],
                        help='Data processing model version')

    args = parser.parse_args()

    if args.source == 'zoomer':
        sys.path.append('src/scrapers/zoomer_scraper')
        import zoomer_scraper.settings as spider_settings
        from zoomer_scraper.spiders.zoomer_spider import ZoomerSpider

        settings = {
            'DOWNLOAD_DELAY': spider_settings.DOWNLOAD_DELAY,
            'CONCURRENT_REQUESTS': spider_settings.CONCURRENT_REQUESTS,
            'CONCURRENT_REQUESTS_PER_DOMAIN': spider_settings.CONCURRENT_REQUESTS_PER_DOMAIN,
            'AUTOTHROTTLE_ENABLED': spider_settings.AUTOTHROTTLE_ENABLED,
            'AUTOTHROTTLE_TARGET_CONCURRENCY': spider_settings.AUTOTHROTTLE_TARGET_CONCURRENCY,
            'AUTOTHROTTLE_START_DELAY': spider_settings.AUTOTHROTTLE_START_DELAY,
            'AUTOTHROTTLE_MAX_DELAY': spider_settings.AUTOTHROTTLE_MAX_DELAY,
            'USER_AGENT': spider_settings.USER_AGENT,
            'LOG_LEVEL': spider_settings.LOG_LEVEL,
            'ROBOTSTXT_OBEY': spider_settings.ROBOTSTXT_OBEY,
            'RANDOMIZE_DOWNLOAD_DELAY': spider_settings.RANDOMIZE_DOWNLOAD_DELAY,
            'DEFAULT_REQUEST_HEADERS': spider_settings.DEFAULT_REQUEST_HEADERS,
            'RETRY_ENABLED': spider_settings.RETRY_ENABLED,
            'RETRY_TIMES': spider_settings.RETRY_TIMES,
            'RETRY_HTTP_CODES': spider_settings.RETRY_HTTP_CODES,
        }

        settings['LOG_FILE'] = 'scrapy.log'
        settings['FEEDS'] = {
            f'data_output/raw/zoomer_{args.category}_{args.max_products}.json': {
                'format': 'json',
                'encoding': 'utf8',
            }
        }

        process = CrawlerProcess(settings)
        logger.info(f"Starting spider for category: {args.category} (max: {args.max_products} products)")

        process.crawl(
            ZoomerSpider,
            category=args.category,
            max_products=args.max_products
        )

        process.start()
        logger.info("Scraping completed successfully")

    else:
        sys.path.append('src/scrapers/ee_scraper')
        from src.scrapers.ee_scraper.ee_scraper import EEScraper

        logger.info("Starting EE scraper using BeautifulSoup...")

        scraper = EEScraper()
        scraper.run()

        logger.info("EE scraping completed successfully")


if __name__ == "__main__":
    main()
