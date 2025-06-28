import os
from datetime import datetime

BOT_NAME = 'zoomer_spider'

SPIDER_MODULES = ['scrapers.zoomer_spider.spiders']
NEWSPIDER_MODULE = 'scrapers.zoomer_spider.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure pipelines
ITEM_PIPELINES = {
    'scrapers.zoomer_spider.pipelines.ValidationPipeline': 300,
    'scrapers.zoomer_spider.pipelines.RawDataPipeline': 400,
    'scrapers.zoomer_spider.pipelines.DatabasePipeline': 500,
}

# Configure middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapers.zoomer_spider.middlewares.UserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapers.zoomer_spider.middlewares.ProxyMiddleware': 350,
}

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = True

# Delay settings
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

# Concurrent requests settings
CONCURRENT_REQUESTS = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Cache settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'

# Output settings
FEEDS = {
    f'data_output/raw/zoomer_raw_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json': {
        'format': 'json',
        'encoding': 'utf8',
    },
    f'data_output/raw/zoomer_raw_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv': {
        'format': 'csv',
        'encoding': 'utf8',
    }
}

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = f'logs/scrapy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

# Database settings
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:your_password@localhost:5432/ecommerce_db')

# Request settings
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ka-GE,ka;q=0.9,en;q=0.8',
}

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# Cookies
COOKIES_ENABLED = True
COOKIES_DEBUG = False

# Extensions
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapers.zoomer_spider.extensions.StatsExtension': 500,
}