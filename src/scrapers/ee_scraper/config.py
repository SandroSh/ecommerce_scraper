"""
EE Scraper Configuration Module

This module contains all configuration settings and constants used by the EE scraper.
It provides centralized configuration management including URLs, selectors,
logging settings, and output preferences.

The configuration is organized into logical sections:
- Base URLs and endpoints
- Default settings and parameters
- HTTP headers for requests
- CSS selectors for HTML parsing
- Logging configuration
- Output file settings

All settings can be modified here to adapt the scraper to different
website structures or requirements.
"""

# Base URL for the EE mobile phones page
BASE_URL = "https://beta.ee.ge/en/mobiluri-telefonebi-da-aqsesuarebi-c320s"

# Default settings
DEFAULT_MAX_PRODUCTS = 0  # scrape all products
DEFAULT_SLEEP_DELAY = 1.0  
DEFAULT_OUTPUT_DIR = "output"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


SELECTORS = {
    # Product container
    "product_container": "div.sc-3ff391e0-5, div.duSkO",
    
    # Product name/title
    "product_name": "h3.sc-3ff391e0-4, h3.iwNALa",
    
    # Product link
    "product_link": "a.sc-3ff391e0-2, a.bgFwDq",
    
    # Price
    "price": "span.sc-3ff391e0-7, span.frTCbv",
    
    # Stock status
    "stock_status": "span.sc-3ff391e0-10, span.gQmggs",
    
    # Fallback selectors
    "fallback_name": "h3, h2, .product-title, .title",
    "fallback_link": "a[href]",
    "fallback_price": "[class*='price'], .price, span:contains('₾')",
    "fallback_container": "div[class*='product'], article, .product-item, .item",
}


LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "ee_scraper.log"
}

OUTPUT_SETTINGS = {
    "json_filename": "ee_products_{timestamp}.json",
    "csv_filename": "ee_products_{timestamp}.csv",
    "timestamp_format": "%Y%m%d_%H%M%S"
} 