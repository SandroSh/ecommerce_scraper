#!/usr/bin/env python3

import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_zoomer_spider():
    """Run the zoomer spider with basic settings"""
    
    from scrapy.crawler import CrawlerProcess
    from scrapy import signals
    from scrapy.signalmanager import dispatcher
    
    # Import spider from the correct location
    sys.path.append('src/scrapers/zoomer_scraper')
    import zoomer_scraper.settings as spider_settings
    from datetime import datetime
    
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
        'FEEDS': {
            f'data_output/raw/zoomer_phones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json': {
                'format': 'json',
                'encoding': 'utf8',
            }
        }
    }
    
    # Results storage
    results = []
    
    def item_scraped(item, response, spider):
        results.append(dict(item))
        print(f"Scraped: {item.get('name', 'Unknown')} - {item.get('price', 'No price')} GEL")
    
    dispatcher.connect(item_scraped, signal=signals.item_scraped)
    
    from zoomer_scraper.spiders.zoomer_spider import ZoomerSpider
    
    process = CrawlerProcess(settings)
    
    # Run spider for phones category - uses MAX_PRODUCTS_TO_SCRAPE from settings.py
    process.crawl(ZoomerSpider, category='phones')  # Will use settings.MAX_PRODUCTS_TO_SCRAPE
    process.start()
    
    print(f"\nTotal items scraped: {len(results)}")
    
    # Save results to file
    if results:
        output_file = f'zoomer_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Results saved to: {output_file}")

if __name__ == "__main__":
    run_zoomer_spider()