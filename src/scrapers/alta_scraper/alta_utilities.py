#!/usr/bin/env python3
"""
Utility functions for Alta.ge scraper
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from selenium.webdriver.common.by import By
from alta_config import AltaConfig


class AltaUtilities:
    """Utility functions for data extraction and processing."""

    @staticmethod
    def extract_price(price_text: str) -> Optional[float]:
        """Extract price from text."""
        if not price_text:
            return None

        price_clean = re.sub(r'[₾$€£¥лари|GEL|USD|EUR|руб|ლ]', '', price_text, flags=re.IGNORECASE)
        price_clean = re.sub(r'\b(price|cost|from|starting|lari|ფასი)\b', '', price_clean, flags=re.IGNORECASE)

        numbers = re.findall(r'\d+[.,]?\d*', price_clean)
        if not numbers:
            return None

        prices = []
        for num in numbers:
            try:
                if ',' in num and '.' not in num:
                    num = num.replace(',', '.')
                elif ',' in num and '.' in num:
                    num = num.replace(',', '')

                price_val = float(num)
                if 10 <= price_val <= 50000:
                    prices.append(price_val)
            except ValueError:
                continue

        return max(prices) if prices else None

    @staticmethod
    def extract_brand_from_name(product_name: str) -> str:
        """Extract brand from product name."""
        if not product_name:
            return "Unknown"

        product_upper = product_name.upper()

        for brand in AltaConfig.BRANDS:
            if brand.upper() in product_upper:
                return brand

        words = product_name.split()
        if words:
            first_word = words[0]
            skip_words = ['new', 'used', 'original', 'refurbished', 'the', 'a', 'ახალი', 'ნაცნობი']
            if first_word.lower() not in skip_words and len(first_word) > 2:
                return first_word

        return "Unknown"

    @staticmethod
    def is_product_element(element) -> bool:
        """Check if element is likely a product element."""
        try:
            text_content = element.text.lower()

            price_patterns = [
                r'\d+[.,]?\d*\s*[₾lari]',
                r'\d+[.,]?\d*\s*[₾]',
                r'\d+[.,]?\d*\s*gel',
                r'\d+[.,]?\d*\s*ლ',
            ]

            has_price = any(re.search(pattern, text_content) for pattern in price_patterns)

            has_product_content = any(word in text_content for word in [
                'samsung', 'apple', 'iphone', 'galaxy', 'buy', 'ყიდვა',
                'laptop', 'computer', 'tv', 'телевизор', 'холодильник'
            ])

            images = element.find_elements(By.TAG_NAME, "img")
            has_image = len(images) > 0
            has_content = len(text_content.strip()) > 10

            return (has_price or has_product_content) and has_content

        except Exception:
            return False

    @staticmethod
    def extract_description(element) -> str:
        """Extract product description."""
        try:
            desc_selectors = [
                '.description', '.desc', '.summary',
                '[class*="description"]', '[class*="desc"]'
            ]

            for selector in desc_selectors:
                try:
                    desc_element = element.find_element(By.CSS_SELECTOR, selector)
                    description = desc_element.text.strip()
                    if description:
                        return description
                except:
                    continue
            return ""
        except:
            return ""

    @staticmethod
    @staticmethod
    def extract_availability(element) -> str:
        """Extract product availability based on keywords in child elements."""
        try:
            # Collect visible text from common containers
            possible_elements = element.find_elements(By.CSS_SELECTOR, 'div, span')

            for el in possible_elements:
                try:
                    text = el.text.strip().lower()
                    if not text:
                        continue

                    if any(keyword in text for keyword in
                           ['in stock', 'available', 'available in stores', 'მარაგშია', 'მიწოდება']):
                        return "Available"
                    elif any(keyword in text for keyword in ['out of stock', 'unavailable', 'არ არის']):
                        return "Out of Stock"

                except Exception:
                    continue

            return "Unknown"
        except Exception:
            return "Unknown"

    @staticmethod
    def save_data(products: List[Dict[str, Any]], category: str) -> str:
        """Save scraped data to JSON file."""
        if not products:
            return ""

        try:
            output_dir = Path("data_output/raw")
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alta_{category}_{len(products)}.json"
            filepath = output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2, default=str)

            return str(filepath)

        except Exception:
            return ""