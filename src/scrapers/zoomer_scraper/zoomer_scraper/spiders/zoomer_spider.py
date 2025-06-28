import scrapy
import time
import random
import re
import json
from datetime import datetime
from scrapy.http import Request
from scrapy.exceptions import CloseSpider
import sys
import os
from ..items import ZoomerScraperItem

# Ensure correct import paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

class ZoomerSpider(scrapy.Spider):
    name = 'zoomer_spider'
    allowed_domains = ['zoommer.ge', 'api.zoommer.ge']
    handle_httpstatus_list = [403, 429]  # Handle rate limiting

    # Category configuration with API endpoints
    CATEGORY_MAP = {
        'phones': {'url': 'https://zoommer.ge/mobiluri-telefonebi-c855', 'api_id': 855, 'name': 'მობილური ტელეფონები'},
        'laptops': {'url': 'https://zoommer.ge/leptopebi-business-leptopi-c563s', 'api_id': 563, 'name': 'Business ლეპტოპი'},
        'gaming_laptops': {'url': 'https://zoommer.ge/leptopebi-gaming-leptopi-c708s', 'api_id': 708, 'name': 'Gaming ლეპტოპი'},
        'classic_laptops': {'url': 'https://zoommer.ge/leptopebi-classic-leptopi-c564s', 'api_id': 564, 'name': 'Classic ლეპტოპი'}
    }

    # Settings are now configured in settings.py

    def __init__(self, category='phones', max_products=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category
        # Use max_products parameter or default
        if max_products is None:
            self.max_products = 50  # Default value
        else:
            self.max_products = int(max_products)
        self.scraped_count = 0
        self.failed_count = 0
        self.category_info = self.CATEGORY_MAP.get(category, self.CATEGORY_MAP['phones'])
        self.category_id = self.category_info['api_id']
        self.api_base_url = 'https://api.zoommer.ge/v1/Products/v3'

    def start_requests(self):
        # Start with API requests for pagination
        page = 1
        api_url = f"{self.api_base_url}?CategoryId={self.category_id}&Page={page}&Limit=14"
        headers = {
            'Accept': 'application/json',
            'Referer': self.category_info['url']
        }
        yield Request(
            api_url,
            callback=self.parse_api_response,
            headers=headers,
            meta={'page': page}
        )

    def parse_category(self, response):
        if response.status in [403, 429]:
            self.logger.warning(f"Rate limited on page {response.meta['page']}")
            yield self.retry_request(response)
            return

        # Extract Next.js SSR data
        next_data = self.extract_nextjs_data(response)
        if next_data and 'initialFilteredProducts' in next_data.get('props', {}).get('pageProps', {}):
            products_data = next_data['props']['pageProps']['initialFilteredProducts']['products']
            self.logger.info(f"Found {len(products_data)} products in SSR data")
            
            for product_data in products_data:
                if self.scraped_count >= self.max_products:
                    raise CloseSpider(f"Reached max products limit: {self.max_products}")
                
                yield self.parse_product_from_data(product_data, self.category)
                self.scraped_count += 1
        else:
            self.logger.error(f"No SSR product data found on {response.url}")

        # Legacy web page parsing - not used with API approach
        pass

    def parse_api_response(self, response):
        """Parse API response with products and handle pagination"""
        if response.status in [403, 429]:
            self.logger.warning(f"Rate limited on API page {response.meta['page']}")
            yield self.retry_request(response)
            return

        try:
            data = response.json()
            products = data.get('products', [])
            products_count = data.get('productsCount', 0)
            current_page = response.meta['page']
            
            self.logger.info(f"API page {current_page}: Found {len(products)} products (total: {products_count})")
            
            # Process products - get detailed info from individual pages
            products_to_process = min(len(products), self.max_products - self.scraped_count)
            
            for i in range(products_to_process):
                product_data = products[i]
                
                # Get product URL using the route field
                product_route = product_data.get('route')
                if product_route:
                    # Make sure route starts with /
                    if not product_route.startswith('/'):
                        product_route = '/' + product_route
                    product_url = f"https://zoommer.ge{product_route}"
                    yield Request(
                        product_url,
                        callback=self.parse_product_detail,
                        meta={
                            'product_data': product_data,
                            'category': self.category
                        }
                    )
                else:
                    # Fallback: use API data only if no route
                    yield self.parse_product_from_api_data(product_data, self.category)
                
                self.scraped_count += 1
            
            if self.scraped_count >= self.max_products:
                self.logger.info(f"Reached max products limit: {self.max_products}")
                return
            
            # Check if we need more pages
            if len(products) == 14 and self.scraped_count < self.max_products:  # 14 is the page limit
                next_page = current_page + 1
                api_url = f"{self.api_base_url}?CategoryId={self.category_id}&Page={next_page}&Limit=14"
                headers = {
                    'Accept': 'application/json',
                    'Referer': self.category_info['url']
                }
                yield Request(
                    api_url,
                    callback=self.parse_api_response,
                    headers=headers,
                    meta={'page': next_page}
                )
            else:
                self.logger.info(f"Finished scraping. Total products: {self.scraped_count}")
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse API response: {e}")
        except Exception as e:
            self.logger.error(f"Error processing API response: {e}")

    def extract_nextjs_data(self, response):
        """Extract Next.js SSR data from script tags"""
        scripts = response.css('script[id="__NEXT_DATA__"]::text').getall()
        if not scripts:
            scripts = response.css('script:contains("__NEXT_DATA__")::text').getall()
        
        for script in scripts:
            try:
                return json.loads(script)
            except json.JSONDecodeError:
                continue
        return None

    def parse_product_from_data(self, product_data, category):
        """Parse product from SSR JSON data"""
        item = ZoomerScraperItem()
        item['source'] = 'zoommer.ge'
        item['name'] = product_data.get('name', '').strip()
        item['price'] = product_data.get('price', 0)
        item['brand'] = product_data.get('categoryName', '').strip()  # Brand is in categoryName
        item['category'] = category
        item['description'] = product_data.get('description', '') or f"Product ID: {product_data.get('id', '')}"
        item['createdat'] = datetime.utcnow().isoformat()
        return item

    def parse_product_from_api_data(self, product_data, category):
        """Parse product from API JSON data"""
        item = ZoomerScraperItem()
        item['source'] = 'zoommer.ge'
        item['name'] = product_data.get('name', '').strip()
        item['price'] = product_data.get('price', 0)
        item['brand'] = product_data.get('categoryName', '').strip()  # Brand is in categoryName field
        item['category'] = category
        item['description'] = product_data.get('description', '') or f"Product ID: {product_data.get('id', '')}"
        item['createdat'] = datetime.utcnow().isoformat()
        return item

    def parse_product_detail(self, response):
        """Parse individual product page for detailed description"""
        product_data = response.meta['product_data']
        category = response.meta['category']
        
        # Extract detailed description from the product page
        description = self.extract_product_description(response)
        
        # Create item with detailed information
        item = ZoomerScraperItem()
        item['source'] = 'zoommer.ge'
        item['name'] = product_data.get('name', '').strip()
        item['price'] = product_data.get('price', 0)
        item['brand'] = product_data.get('categoryName', '').strip()
        item['category'] = category
        item['description'] = description or product_data.get('description', '') or f"Product ID: {product_data.get('id', '')}"
        item['createdat'] = datetime.utcnow().isoformat()
        
        yield item

    def extract_product_description(self, response):
        """Extract detailed description from product page"""
        
        # First, try to get specifications as primary description source
        specs = self.extract_specifications(response)
        if specs:
            # Create a meaningful description from specs
            key_specs = []
            for key, value in list(specs.items())[:8]:  # Top 8 specs
                key_specs.append(f"{key}: {value}")
            if key_specs:
                return "; ".join(key_specs)[:500]
        
        # Fallback: try traditional description selectors
        description_selectors = [
            '.product-description',
            '.description',
            '[class*="description"]',
            '.product-details',
            '.product-info',
            '.product-content',
            '.product-overview'
        ]
        
        description_parts = []
        
        # Try each selector
        for selector in description_selectors:
            elements = response.css(selector)
            if elements:
                # Extract text from all matching elements
                texts = elements.css('::text').getall()
                clean_texts = [text.strip() for text in texts if text.strip()]
                if clean_texts:
                    description_parts.extend(clean_texts)
                    break
        
        # If no description found, try to extract from Next.js data
        if not description_parts:
            try:
                scripts = response.css('script:contains("__NEXT_DATA__")::text').getall()
                for script in scripts:
                    data = json.loads(script)
                    page_props = data.get('props', {}).get('pageProps', {})
                    product_info = page_props.get('product', {})
                    desc = product_info.get('description') or product_info.get('longDescription')
                    if desc:
                        description_parts = [desc.strip()]
                        break
            except:
                pass
        
        # Join all description parts
        if description_parts:
            return ' '.join(description_parts)[:500]  # Limit to 500 chars
        
        return None

    def extract_specifications(self, response):
        """Extract product specifications from product page"""
        specs = {}
        
        # Try to get specifications from tables
        tables = response.css('table')
        for table in tables:
            rows = table.css('tr')
            for row in rows:
                cells = row.css('td')
                if len(cells) >= 2:
                    key = cells[0].css('::text').get()
                    value = cells[1].css('::text').get()
                    if key and value:
                        key = key.strip().rstrip(':')
                        value = value.strip()
                        if key and value:
                            specs[key] = value
        
        return specs

    def parse_product(self, response):
        """Legacy method for individual product pages (not used with SSR data)"""
        self.scraped_count += 1
        item = ZoomerScraperItem()
        item['source'] = 'zoommer.ge'
        item['name'] = self.extract_text(response, 'h1.product-title::text')
        item['price'] = self.extract_price(response, '.current-price::text')
        item['brand'] = self.extract_text(response, '.manufacturer a::text')
        item['category'] = response.meta['category']
        item['description'] = self.extract_description(response)
        item['createdat'] = datetime.utcnow().isoformat()
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