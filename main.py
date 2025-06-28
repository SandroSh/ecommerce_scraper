# main.py
import argparse
import os
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from src.scrapers.zoomer_scraper.zoomer_scraper.spiders.zoomer_spider import ZoomerSpider
# from src.data.database import init_db


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

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run Zoomer.ge product scraper')
    parser.add_argument('--category', type=str, default='phones',
                        choices=['phones', 'fridges', 'laptops', 'tvs'],
                        help='Product category to scrape')
    parser.add_argument('--max_products', type=int, default=100,
                        help='Maximum number of products to scrape')

    args = parser.parse_args()

    # Configure Scrapy settings
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapers.zoomer_scraper.settings'
    settings = get_project_settings()

    # Override settings if needed
    settings.set('LOG_FILE', 'scrapy.log')
    settings.set('FEEDS', {
        f'data_output/zoomer_{args.category}_{args.max_products}.json': {
            'format': 'json',
            'encoding': 'utf8',
        }
    })

    # Configure database URL from environment variable
    if 'DATABASE_URL' in os.environ:
        settings.set('DATABASE_URL', os.environ['DATABASE_URL'])
        logger.info("Using database URL from environment variable")

    # Start crawling process
    process = CrawlerProcess(settings)
    logger.info(f"Starting spider for category: {args.category} (max: {args.max_products} products)")

    process.crawl(
        ZoomerSpider,
        category=args.category,
        max_products=args.max_products
    )

    process.start()
    logger.info("Scraping completed successfully")


if __name__ == "__main__":
    main()