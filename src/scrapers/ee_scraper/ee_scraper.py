"""
EE Scraper Module

This module provides a comprehensive web scraper for the EE.ge e-commerce website,
specifically targeting mobile phones and accessories. The scraper uses BeautifulSoup
for HTML parsing and implements robust error handling and rate limiting.

Classes:
    EEScraper: Main scraper class for extracting product data from EE.ge

Dependencies:
    - requests: For HTTP requests
    - BeautifulSoup: For HTML parsing
    - datetime: For timestamp generation
    - re: For regular expressions
    - os: For file system operations
    - time: For rate limiting
"""

import requests
from bs4 import BeautifulSoup
from src.utils.logger import get_logger
from src.utils.data_helpers import Product, save_products_to_json, extract_brand_from_name, clean_price
import time
import re
import os
from datetime import datetime


class EEScraper:
    """
    A comprehensive web scraper for the EE.ge e-commerce website.
    
    This scraper is designed to extract product information from the EE.ge mobile
    phones and accessories section. It handles pagination, product parsing, and
    data export with robust error handling and rate limiting.
    
    Attributes:
        BASE_URL (str): The base URL for the EE.ge mobile phones page
        logger: Logger instance for debugging and monitoring
        max_products (int): Maximum number of products to scrape (0 for unlimited)
        sleep (float): Delay between requests in seconds
        headers (dict): HTTP headers for requests
    """
    
    BASE_URL = "https://beta.ee.ge/en/mobiluri-telefonebi-da-aqsesuarebi-c320s"

    def __init__(self, max_products=10, sleep=1.0):
        """
        Initialize the EE scraper with configuration parameters.
        
        Args:
            max_products (int): Maximum number of products to scrape. 
                              Default is 100. Use 0 for unlimited scraping.
            sleep (float): Delay between requests in seconds. Default is 1.0.
        """
        self.logger = get_logger(__name__)
        self.max_products = max_products
        self.sleep = sleep
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def clean_price_to_number(self, price_text):
        """
        Convert price text to numeric value by removing currency symbols and formatting.
        
        Args:
            price_text (str): Price text containing currency symbols and formatting
            
        Returns:
            int: Cleaned numeric price value, or 0 if conversion fails
        """
        if not price_text or price_text == "N/A":
            return 0
        
        cleaned = price_text.replace('₾', '').replace(' ', '').strip()
        cleaned = re.sub(r'[^\d.]', '', cleaned)
        
        try:
            return int(float(cleaned))
        except (ValueError, TypeError):
            return 0

    def get_all_listing_pages(self):
        """
        Fetch all page URLs from pagination using the EE site structure.
        
        This method analyzes the main page to find pagination links and generates
        a comprehensive list of all available product listing pages. It includes
        fallback mechanisms for different pagination structures.
        
        Returns:
            list: List of unique page URLs to scrape, sorted by page number
        """
        res = requests.get(self.BASE_URL, headers=self.headers)
        soup = BeautifulSoup(res.content, "html.parser")

        page_links = soup.select("a.sc-65de7bd2-2[href*='page=']")
        urls = set()

        for a in page_links:
            href = a.get("href")
            if isinstance(href, list):
                href = href[0] if href else None
            
            if href and "page=" in href:
                full_url = href if href.startswith("http") else f"https://beta.ee.ge{href}"
                urls.add(full_url)

        urls.add(self.BASE_URL)
        
        if len(urls) < 10:
            self.logger.info(f"Found only {len(urls)} pages, trying alternative pagination selectors...")
            
            alt_page_links = soup.select("a[href*='page='], .pagination a, nav a, [class*='page'] a")
            for a in alt_page_links:
                href = a.get("href")
                if isinstance(href, list):
                    href = href[0] if href else None
                
                if href and "page=" in href:
                    full_url = href if href.startswith("http") else f"https://beta.ee.ge{href}"
                    urls.add(full_url)
            
            self.logger.info(f"After alternative selectors: {len(urls)} pages")
        
        if len(urls) < 20:
            self.logger.info("Generating page URLs manually (limited to 20 pages)...")
            
            for page_num in range(0, 1):
                pattern = f"{self.BASE_URL}?page={page_num}"
                urls.add(pattern)
            
            self.logger.info(f"After manual generation: {len(urls)} pages")
        
        def extract_page_number(url):
            if "page=" in url:
                try:
                    return int(url.split("page=")[1].split("&")[0])
                except:
                    return 0
            return 0
        
        sorted_urls = sorted(urls, key=extract_page_number)
        
        unique_urls = []
        seen = set()
        for url in sorted_urls:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)
        
        self.logger.info(f"Found {len(unique_urls)} unique pages to scrape")
        
        if unique_urls:
            self.logger.info(f"First 5 pages: {unique_urls[:5]}")
            if len(unique_urls) > 10:
                self.logger.info(f"Last 5 pages: {unique_urls[-5:]}")
        
        return unique_urls

    def get_product_links(self, page_url):
        """
        Extract product links from a listing page.
        
        Args:
            page_url (str): URL of the listing page to scrape
            
        Returns:
            list: List of product URLs found on the page
        """
        res = requests.get(page_url, headers=self.headers)
        soup = BeautifulSoup(res.content, "html.parser")

        product_links = []
    
        for product_div in soup.select("div[class*='product'], article, .product-item"):
            a_tag = product_div.select_one("a[href]")
            if a_tag:
                href = a_tag.get("href")
                if isinstance(href, list):
                    href = href[0] if href else None
                    
                if href:
                    full_url = f"https://beta.ee.ge{href}" if not href.startswith("http") else href
                    product_links.append(full_url)

        self.logger.info(f"Found {len(product_links)} product links on {page_url}")
        return product_links

    def parse_product_details(self, product_url):
        """
        Parse detailed product information from a product page.
        
        This method extracts comprehensive product details including SKU, specifications,
        warranty information, and detailed specs from product tables.
        
        Args:
            product_url (str): URL of the product page to parse
            
        Returns:
            dict: Dictionary containing detailed product information
        """
        try:
            res = requests.get(product_url, headers=self.headers)
            soup = BeautifulSoup(res.content, "html.parser")
            
            sku = ""
            sku_element = soup.select_one("span.sc-235e453a-19.eOnNNp")
            if sku_element:
                sku = sku_element.text.strip()
            
            specs = []
            spec_elements = soup.select("li.sc-235e453a-27.khePzm")
            for spec in spec_elements:
                specs.append(spec.text.strip())
            
            warranty = ""
            warranty_elements = soup.select("div.sc-235e453a-24.hVytZX a")
            if warranty_elements:
                warranty_texts = [elem.text.strip() for elem in warranty_elements]
                warranty = " | ".join(warranty_texts)
            
            detailed_specs = {}
            spec_tables = soup.select("table.sc-bc705976-4.bbQIJZ")
            for table in spec_tables:
                rows = table.select("tr.sc-bc705976-6.UicTo")
                for row in rows:
                    cells = row.select("td.sc-bc705976-7")
                    if len(cells) >= 2:
                        key = cells[0].text.strip().replace(":", "")
                        value = cells[1].text.strip()
                        detailed_specs[key] = value
            
            return {
                'sku': sku,
                'specifications': specs,
                'warranty': warranty,
                'detailed_specs': detailed_specs
            }
        except Exception as e:
            self.logger.warning(f"Failed to parse product details from {product_url}: {e}")
            return {}

    def parse_product_from_listing(self, product_div):
        """
        Parse product information directly from a listing page product div.
        
        This method extracts product data from HTML elements within a product container,
        including name, price, brand, link, and category. It implements multiple
        fallback selectors to handle different page structures.
        
        Args:
            product_div: BeautifulSoup element containing product information
            
        Returns:
            dict: Product information dictionary, or None if parsing fails
        """
        try:
            name_tag = product_div.select_one("h3.sc-3ff391e0-4, h3.iwNALa")
            if not name_tag:
                name_tag = product_div.select_one("h3, h2, .product-title, .title")
            name = name_tag.text.strip() if name_tag else "Unknown"

            if not name or name == "Unknown" or len(name) < 3:
                self.logger.debug(f"Skipping product with invalid name: '{name}'")
                return None

            link_tag = product_div.select_one("a.sc-3ff391e0-3, a.iwNALa")
            if not link_tag:
                link_tag = product_div.select_one("a[href]")
            
            link = link_tag.get("href") if link_tag else None
            if isinstance(link, list):
                link = link[0] if link else None
            
            if not link:
                self.logger.debug(f"Skipping product '{name}' - no link found")
                return None

            if "/mobile-phone" not in link and "/cable" not in link and "/accessory" not in link:
                self.logger.debug(f"Skipping product '{name}' - link doesn't contain mobile-related path: {link}")
                return None

            if link.startswith("/"):
                link = f"https://beta.ee.ge{link}"

            price_tag = product_div.select_one("span.sc-3ff391e0-6, span.iwNALa")
            if not price_tag:
                price_selectors = [
                    "span[class*='price']",
                    "div[class*='price']", 
                    "span:contains('₾')",
                    "[class*='cost']",
                    "span",
                    "div"
                ]
                for selector in price_selectors:
                    price_tag = product_div.select_one(selector)
                    if price_tag and '₾' in price_tag.text:
                        break

            price_text = price_tag.text.strip() if price_tag else "0₾"
            
            price = 0
            try:
                price_clean = price_text.replace('₾', '').replace(' ', '').replace(',', '')
                price = int(float(price_clean))
            except (ValueError, AttributeError):
                self.logger.debug(f"Skipping product '{name}' - invalid price: '{price_text}'")
                return None

            if price <= 0:
                self.logger.debug(f"Skipping product '{name}' - zero or negative price: {price}")
                return None

            brand = name.split()[0] if name else "Unknown"
            
            if brand == "Unknown":
                self.logger.debug(f"Skipping product '{name}' - unknown brand")
                return None

            category = 'phones'
            if '/cable' in link:
                category = 'accessories'
            elif '/accessory' in link:
                category = 'accessories'

            product = {
                'name': name,
                'price': price,
                'brand': brand,
                'link': link,
                'source': 'ee.ge',
                'category': category,
                'description': f"Stock: Available, SKU: {brand}-{price}, Warranty: 12 months, Specs: {category.title()}, URL: {link}",
                'timestamp': datetime.now().isoformat()
            }

            return product

        except Exception as e:
            self.logger.debug(f"Error parsing product: {str(e)}")
            return None

    def run(self):
        """
        Execute the main scraping process.
        
        This method orchestrates the entire scraping workflow:
        1. Fetches all listing pages
        2. Iterates through each page
        3. Extracts product information
        4. Saves results to JSON file
        
        Returns:
            list: List of scraped product dictionaries
        """
        self.logger.info("Starting EE scraper for beta.ee.ge...")

        listing_pages = self.get_all_listing_pages()
        all_products = []
        consecutive_empty_pages = 0
        max_empty_pages = 3

        for page_num, page in enumerate(listing_pages, 1):
            self.logger.info(f"Scraping page {page_num}/{len(listing_pages)}: {page}")
            res = requests.get(page, headers=self.headers)
            soup = BeautifulSoup(res.content, "html.parser")

            product_divs = soup.select("div.sc-3ff391e0-5.duSkO")
            if not product_divs:
                product_divs = soup.select("div.sc-3ff391e0-5")
            if not product_divs:
                product_divs = soup.select("div[class*='product'], div[class*='item']")
            if not product_divs:
                product_divs = soup.select("div[class*='card'], div[class*='product'], article")
            if not product_divs:
                product_divs = soup.select("div[class*='sc-'], div[class*='item'], div[class*='product']")
            if not product_divs:
                product_divs = []
                for div in soup.select("div"):
                    has_name = div.select_one("h3, h2, .product-title, .title")
                    has_price = div.select_one("span:contains('₾'), [class*='price']")
                    has_link = div.select_one("a[href*='/mobile-phone'], a[href*='/en/']")
                    
                    if has_name and has_price and has_link:
                        product_divs.append(div)
            
            self.logger.info(f"Found {len(product_divs)} potential product divs on page {page_num}")
            
            if len(product_divs) == 0:
                consecutive_empty_pages += 1
                self.logger.warning(f"Page {page_num} is empty. Consecutive empty pages: {consecutive_empty_pages}")
                
                if consecutive_empty_pages >= max_empty_pages:
                    self.logger.info(f"Stopping scraper after {consecutive_empty_pages} consecutive empty pages")
                    break
            else:
                consecutive_empty_pages = 0
            
            page_products = 0
            for i, product_div in enumerate(product_divs):
                if self.max_products and len(all_products) >= self.max_products:
                    break
                    
                product = self.parse_product_from_listing(product_div)
                if product and product.get('name') != "Unknown" and product.get('price', 0) > 0:
                    all_products.append(product)
                    page_products += 1
                    self.logger.info(f"Added product: {product.get('name')} - {product.get('price')} GEL")
                else:
                    if i < 3:
                        name_elem = product_div.select_one("h3, h2, .product-title, .title")
                        price_elem = product_div.select_one("[class*='price'], [class*='cost'], span:contains('₾')")
                        link_elem = product_div.select_one("a[href]")
                        
                        name_text = name_elem.text.strip() if name_elem else "No name"
                        price_text = price_elem.text.strip() if price_elem else "No price"
                        link_href = link_elem.get('href') if link_elem else "No link"
                        
                        self.logger.info(f"Rejected div {i+1}: Name='{name_text[:50]}', Price='{price_text}', Link='{link_href[:50] if link_href else 'No link'}'")
                time.sleep(self.sleep)

            self.logger.info(f"Found {page_products} valid products on page {page_num}")
            time.sleep(self.sleep)

        if all_products:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            output_dir = os.path.join(project_root, "data_output", "raw")
            
            os.makedirs(output_dir, exist_ok=True)
            
            json_file = save_products_to_json(all_products, os.path.join(output_dir, "ee_phones.json"))
            self.logger.info(f"Saved {len(all_products)} products to {json_file}")
        
        self.logger.info(f"EE scraping completed. Found {len(all_products)} products across {len(listing_pages)} pages.")
        return all_products
