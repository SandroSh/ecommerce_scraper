import argparse
import os
import sys
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# Import will be done after setting up paths


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
    parser.add_argument('--max_products', type=int, default=10,
                        help='Maximum number of products to scrape')
    parser.add_argument('--model_version', type=str, default='v1',
                        choices=['v1', 'v2', 'v3'],
                        help='Data processing model version')

    args = parser.parse_args()

    # Add the correct path and import spider
    sys.path.append('src/scrapers/zoomer_scraper')
    import zoomer_scraper.settings as spider_settings
    from zoomer_scraper.spiders.zoomer_spider import ZoomerSpider

    # Create settings dict with our values
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

    # Add feeds to settings
    settings['LOG_FILE'] = 'scrapy.log'
    settings['FEEDS'] = {
        f'data_output/raw/zoomer_{args.category}_{args.max_products}.json': {
            'format': 'json',
            'encoding': 'utf8',
        }
    }

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