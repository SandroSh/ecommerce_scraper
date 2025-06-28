import os
from datetime import datetime

BOT_NAME = 'zoomer_spider'

SPIDER_MODULES = ['zoomer_scraper.spiders']
NEWSPIDER_MODULE = 'zoomer_scraper.spiders'

# Performance settings
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 3

# Basic settings
ROBOTSTXT_OBEY = True
RANDOMIZE_DOWNLOAD_DELAY = True

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# Output settings (will be overridden by main.py and run_spider.py)
# FEEDS = {}

# Request settings
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ka-GE,ka;q=0.9,en;q=0.8',
}

# User Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# Logging
LOG_LEVEL = 'INFO'

# Disable telnet console (not used)
# TELNETCONSOLE_ENABLED = False