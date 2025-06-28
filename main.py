import argparse
import os
import sys
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from src.scrapers.zoomer_scraper.zoomer_scraper.spiders.zoomer_spider import ZoomerSpider


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )


def main():
    configure_logging()
    logger = logging.getLogger(__name__)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run E-commerce product scraper')
    parser.add_argument('--category', type=str, default='phones',
                        choices=['phones', 'fridges', 'laptops', 'tvs'],
                        help='Product category to scrape')
    parser.add_argument('--max_products', type=int, default=100,
                        help='Maximum number of products to scrape')
    parser.add_argument('--model_version', type=str, default='v1',
                        choices=['v1', 'v2', 'v3'],
                        help='Data processing model version')

    args = parser.parse_args()

    # Configure Scrapy settings
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapers.zoomer_scraper.settings'
    os.environ['MODEL_VERSION'] = args.model_version  # Pass model version

    settings = get_project_settings()

    # Override settings
    settings.set('LOG_FILE', 'scrapy.log')
    settings.set('FEEDS', {
        f'data_output/raw/zoomer_{args.category}_{args.max_products}.jsonl': {
            'format': 'jsonlines',
            'encoding': 'utf8',
        }
    })

    # Start crawling process
    process = CrawlerProcess(settings)
    logger.info(f"Starting spider for category: {args.category} (max: {args.max_products} products)")

    # Import spider after setting up environment

    process.crawl(
        ZoomerSpider,
        category=args.category,
        max_products=args.max_products
    )

    process.start()
    logger.info("Scraping completed successfully")


if __name__ == "__main__":
    main()