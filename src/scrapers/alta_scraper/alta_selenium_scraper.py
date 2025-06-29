#!/usr/bin/env python3
"""
Enhanced scraper class for Alta.ge with category-specific selectors
"""

import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from alta_config import AltaConfig
from alta_utilities import AltaUtilities


class AltaScraper:
    """Enhanced Selenium-based scraper for alta.ge with category-specific logic."""

    def __init__(self, headless: bool = True, max_products: int = 50, debug: bool = False):
        self.max_products = max_products
        self.headless = headless
        self.debug = debug
        self.driver = None
        self.wait = None
        self.scraped_data = []
        self.current_category = None

        self.logger = AltaConfig.setup_logging(debug)

    def setup_driver(self) -> None:
        """Setup Chrome WebDriver."""
        try:
            service = Service(ChromeDriverManager().install())
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument('--headless=new')

            for option in AltaConfig.CHROME_OPTIONS:
                chrome_options.add_argument(option)

            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f'--user-agent={AltaConfig.USER_AGENT}')

            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(AltaConfig.PAGE_LOAD_TIMEOUT)
            self.wait = WebDriverWait(self.driver, AltaConfig.ELEMENT_TIMEOUT)

            self.logger.info("✅ Chrome WebDriver initialized successfully")

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize WebDriver: {e}")
            raise

    def test_site_accessibility(self) -> bool:
        """Test if alta.ge is accessible."""
        try:
            self.logger.info("🔍 Testing site accessibility...")
            self.driver.get(AltaConfig.BASE_URL)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            current_url = self.driver.current_url
            page_title = self.driver.title

            self.logger.info(f"📍 Current URL: {current_url}")
            self.logger.info(f"📄 Page title: {page_title}")

            page_source = self.driver.page_source.lower()
            blocking_indicators = [
                'cloudflare', 'access denied', 'blocked', 'captcha',
                'security check', 'please wait', 'checking your browser'
            ]

            for indicator in blocking_indicators:
                if indicator in page_source:
                    self.logger.warning(f"⚠️ Possible blocking detected: {indicator}")
                    return False

            self.logger.info("✅ Site is accessible")
            return True

        except TimeoutException:
            self.logger.error("❌ Timeout accessing the site")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error accessing site: {e}")
            return False

    def find_product_elements(self, category: str):
        """Find product elements using category-specific selectors."""
        product_elements = []

        # Get category-specific selectors first
        category_selectors = AltaConfig.get_category_selectors(category)
        container_selectors = category_selectors.get('container', AltaConfig.PRODUCT_SELECTORS)

        # Try category-specific selectors first
        for selector in container_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    self.logger.info(f"📦 Found {len(elements)} elements with category selector: {selector}")
                    filtered_elements = [e for e in elements if AltaUtilities.is_product_element(e)]

                    if filtered_elements:
                        self.logger.info(f"📦 Filtered to {len(filtered_elements)} actual product elements")
                        product_elements = filtered_elements
                        break
            except Exception as e:
                self.logger.debug(f"Error with category selector {selector}: {e}")
                continue

        # Fall back to general selectors if category-specific didn't work
        if not product_elements:
            self.logger.info("🔄 Falling back to general selectors...")
            for selector in AltaConfig.PRODUCT_SELECTORS:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        self.logger.info(f"📦 Found {len(elements)} elements with general selector: {selector}")
                        filtered_elements = [e for e in elements if AltaUtilities.is_product_element(e)]

                        if filtered_elements:
                            self.logger.info(f"📦 Filtered to {len(filtered_elements)} actual product elements")
                            product_elements = filtered_elements
                            break
                except Exception as e:
                    self.logger.debug(f"Error with general selector {selector}: {e}")
                    continue

        return product_elements

    def extract_product_info(self, element, category: str) -> Optional[Dict[str, Any]]:
        """Extract product information from element using category-specific selectors."""
        try:
            product_data = {}

            # Get category-specific selectors
            category_selectors = AltaConfig.get_category_selectors(category)
            name_selectors = category_selectors.get('name', AltaConfig.NAME_SELECTORS)
            price_selectors = category_selectors.get('price', AltaConfig.PRICE_SELECTORS)

            # Extract name using category-specific selectors first
            product_name = self._extract_name(element, name_selectors)
            if not product_name:
                return None

            product_data['name'] = product_name

            # Extract price using category-specific selectors
            price = self._extract_price(element, price_selectors)
            product_data['price'] = price
            product_data['brand'] = AltaUtilities.extract_brand_from_name(product_name)

            # Extract URL
            product_data['product_url'] = self._extract_url(element, category)

            # Extract image
            product_data['image_url'] = self._extract_image(element)

            # Extract additional info
            product_data['description'] = AltaUtilities.extract_description(element)
            product_data['availability'] = AltaUtilities.extract_availability(element)

            return product_data

        except Exception as e:
            self.logger.debug(f"Error extracting product info: {e}")
            return None

    def _extract_name(self, element, name_selectors: List[str]) -> Optional[str]:
        """Extract product name using provided selectors."""
        # Try category-specific selectors first
        for selector in name_selectors:
            try:
                name_element = element.find_element(By.CSS_SELECTOR, selector)
                text = name_element.text.strip() or name_element.get_attribute('title')
                if text and len(text) > 5:
                    return text
            except:
                continue

        # Fallback to general name extraction
        try:
            links = element.find_elements(By.TAG_NAME, "a")
            for link in links:
                title = link.get_attribute('title')
                text = link.text.strip()
                if title and len(title) > 5:
                    return title
                elif text and len(text) > 5:
                    return text
        except:
            pass

        return None

    def _extract_price(self, element, price_selectors: List[str]) -> Optional[float]:
        """Extract price using provided selectors."""
        # Try category-specific price selectors first
        for selector in price_selectors:
            try:
                price_element = element.find_element(By.CSS_SELECTOR, selector)
                price_text = price_element.text.strip()
                if price_text:
                    extracted_price = AltaUtilities.extract_price(price_text)
                    if extracted_price:
                        return extracted_price
            except:
                continue

        # Fallback to extracting from entire element text
        return AltaUtilities.extract_price(element.text)

    def _extract_url(self, element, category: str) -> Optional[str]:
        """Extract product URL."""
        try:
            # Try category-specific link patterns first
            category_patterns = {
                'laptops': ['a[href*="/laptop/"]', 'a[href*="/notebooks/"]'],
                'tvs': ['a[href*="/tv/"]', 'a[href*="/television/"]'],
                'fridges': ['a[href*="/refrigerator/"]', 'a[href*="/fridge/"]'],
                'phones': ['a[href*="/mobile-phones/"]', 'a[href*="/smartphone/"]']
            }

            patterns = category_patterns.get(category, [])
            for pattern in patterns:
                try:
                    link_element = element.find_element(By.CSS_SELECTOR, pattern)
                    href = link_element.get_attribute('href')
                    if href:
                        if not href.startswith('http'):
                            href = f"{AltaConfig.BASE_URL}{href}"
                        return href
                except:
                    continue

            # Fall back to general link selectors
            for selector in AltaConfig.LINK_SELECTORS:
                try:
                    link_element = element.find_element(By.CSS_SELECTOR, selector)
                    href = link_element.get_attribute('href')
                    if href:
                        if not href.startswith('http'):
                            href = f"{AltaConfig.BASE_URL}{href}"
                        return href
                except:
                    continue

        except Exception as e:
            self.logger.debug(f"Error extracting URL: {e}")

        return None

    def _extract_image(self, element) -> Optional[str]:
        """Extract product image URL."""
        try:
            img_element = element.find_element(By.TAG_NAME, "img")
            img_src = img_element.get_attribute('src') or img_element.get_attribute('data-src')
            if img_src and not img_src.startswith('http'):
                img_src = f"{AltaConfig.BASE_URL}{img_src}"
            return img_src
        except:
            return None

    def scrape_products(self, category_url: str, category: str) -> List[Dict[str, Any]]:
        """Scrape products from category page."""
        products = []
        self.current_category = category

        try:
            self.logger.info(f"🔍 Loading {category} category page: {category_url}")
            self.driver.get(category_url)
            time.sleep(5)

            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(3)
            except TimeoutException:
                self.logger.warning("Timeout waiting for page body")

            # Use category-specific element finding
            product_elements = self.find_product_elements(category)

            if not product_elements:
                self.logger.warning(f"❌ No product elements found for {category}")
                return products

            self.logger.info(f"📊 Processing {len(product_elements)} product elements for {category}...")

            for i, element in enumerate(product_elements):
                if len(products) >= self.max_products:
                    break

                try:
                    # Use category-specific extraction
                    product_data = self.extract_product_info(element, category)

                    if product_data and product_data.get('name'):
                        product_data.update({
                            'source': 'alta.ge',
                            'category': category,
                            'createdat': datetime.now(timezone.utc).isoformat()
                        })

                        products.append(product_data)
                        self.logger.info(f"✅ [{len(products)}] {product_data['name'][:60]}...")
                        time.sleep(0.5)

                except Exception as e:
                    self.logger.debug(f"Error processing element {i}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"❌ Error scraping {category} products: {e}")

        return products

    def run(self, category: str) -> str:
        """Main scraping method."""
        try:
            self.logger.info(f"🚀 Starting Enhanced Alta.ge scraper for category: {category}")

            self.setup_driver()

            if not self.test_site_accessibility():
                self.logger.error("❌ Site is not accessible")
                return ""

            category_path = AltaConfig.CATEGORY_URLS.get(category)
            if not category_path:
                self.logger.error(f"❌ Unknown category: {category}")
                return ""

            category_url = f"{AltaConfig.BASE_URL}{category_path}"
            products = self.scrape_products(category_url, category)

            if not products:
                self.logger.warning(f"⚠️ No products were scraped from {category}")
                return ""

            filepath = AltaUtilities.save_data(products, category)
            self.logger.info(f"🎉 Successfully scraped {len(products)} products from {category}")
            return filepath

        except Exception as e:
            self.logger.error(f"💥 Scraping failed with error: {e}")
            return ""

        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("🔒 WebDriver closed")