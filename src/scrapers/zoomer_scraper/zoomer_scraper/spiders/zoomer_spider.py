import scrapy
import time
import random
import re
from datetime import datetime
from scrapy.http import Request
from scrapy.exceptions import CloseSpider
import sys
import os

# Ensure correct import paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

class ZoomerSpider(scrapy.Spider):
    name = 'zoomer_spider'
    allowed_domains = ['zoomer.ge']
    handle_httpstatus_list = [403, 429]  # Handle rate limiting

    # Category configuration
    CATEGORY_MAP = {
        'phones': ('https://zoomer.ge/ka/category/29', 'მობილური ტელეფონები'),
        'fridges': ('https://zoomer.ge/ka/category/refrigerators', 'მაცივრები'),
        'laptops': ('https://zoomer.ge/ka/category/laptops', 'ლეპტოპები'),
        'tvs': ('https://zoomer.ge/ka/category/tv', 'ტელევიზორები')
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 2.5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 15,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    def __init__(self, category='phones', max_products=1000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category
        self.max_products = int(max_products)
        self.scraped_count = 0
        self.failed_count = 0
        self.start_urls = [self.CATEGORY_MAP.get(category, self.CATEGORY_MAP['phones'])[0]]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse_category, meta={'page': 1})

    def parse_category(self, response):
        if response.status in [403, 429]:
            self.logger.warning(f"Rate limited on page {response.meta['page']}")
            yield self.retry_request(response)
            return

        # Extract products
        products = response.css('div.product-item')
        if not products:
            self.logger.error(f"No products found on {response.url}")
            return

        for product in products:
            if self.scraped_count >= self.max_products:
                raise CloseSpider(f"Reached max products limit: {self.max_products}")

            link = product.css('a::attr(href)').get()
            if link:
                yield response.follow(
                    link,
                    callback=self.parse_product,
                    meta={'category': self.category}
                )

        # Pagination
        current_page = response.meta['page']
        next_page = current_page + 1
        next_url = f"{response.url.split('?')[0]}?page={next_page}"

        if next_page <= 50:  # Safety limit
            yield response.follow(
                next_url,
                callback=self.parse_category,
                meta={'page': next_page}
            )

    def parse_product(self, response):
        self.scraped_count += 1
        item = {
            'url': response.url,
            'scraped_at': datetime.utcnow().isoformat(),
            'category': response.meta['category'],
            'name': self.extract_text(response, 'h1.product-title::text'),
            'price': self.extract_price(response, '.current-price::text'),
            'brand': self.extract_text(response, '.manufacturer a::text'),
            'description': self.extract_description(response),
            'specifications': self.extract_specs(response),
            'images': self.extract_images(response),
            'availability': bool(response.css('.stock-available')),
            'rating': response.css('.rating::attr(data-rating)').get(),
            'raw_html': response.text[:50000]  # Store partial HTML for debugging
        }
        yield item

    def retry_request(self, response):
        retry_count = response.meta.get('retry_count', 0) + 1
        if retry_count > 3:
            self.logger.error(f"Max retries exceeded for {response.url}")
            return None

        delay = random.uniform(10, 30)
        self.logger.info(f"Retrying {response.url} in {delay:.1f}s (attempt {retry_count})")
        time.sleep(delay)

        return response.request.replace(
            meta={**response.meta, 'retry_count': retry_count},
            dont_filter=True
        )

    def extract_text(self, response, selector):
        return response.css(selector).get('').strip() or None

    def extract_price(self, response, selector):
        price_text = response.css(selector).get('')
        if not price_text:
            return None
        return float(re.sub(r'[^\d.]', '', price_text.replace(',', '.')))

    def extract_description(self, response):
        return '\n'.join([
            p.strip() for p in
            response.css('.product-description ::text').getall()
            if p.strip()
        ]) or None

    def extract_specs(self, response):
        specs = {}
        for row in response.css('.specifications tr'):
            key = row.css('td:first-child::text').get('').strip()
            value = row.css('td:last-child::text').get('').strip()
            if key and value:
                specs[key] = value
        return specs or None

    def extract_images(self, response):
        return [
                   response.urljoin(img)
                   for img in response.css('.product-gallery img::attr(src)').getall()
               ][:5]  # Max 5 images