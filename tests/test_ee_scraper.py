"""
Unit tests for EE scraper module.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scrapers.ee_scraper.ee_scraper import EEScraper


class TestEEScraper(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.scraper = EEScraper(max_products=10, sleep=0.1)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test scraper initialization."""
        default_scraper = EEScraper()
        self.assertEqual(default_scraper.max_products, 100)
        self.assertEqual(default_scraper.sleep, 1.0)
        
        custom_scraper = EEScraper(max_products=50, sleep=2.0)
        self.assertEqual(custom_scraper.max_products, 50)
        self.assertEqual(custom_scraper.sleep, 2.0)
    
    def test_clean_price(self):
        """Test price cleaning."""
        test_cases = [
            ("999₾", 999),
            ("1,299 ₾", 1299),
            ("N/A", 0),
            ("", 0),
            (None, 0)
        ]
        
        for input_price, expected in test_cases:
            result = self.scraper.clean_price_to_number(input_price)
            self.assertEqual(result, expected)
    
    @patch('requests.get')
    def test_get_listing_pages(self, mock_get):
        """Test getting listing pages."""
        mock_response = MagicMock()
        mock_response.content = '''
        <html><body>
            <a href="?page=1" class="sc-65de7bd2-2">Page 1</a>
            <a href="?page=2" class="sc-65de7bd2-2">Page 2</a>
        </body></html>
        '''
        mock_get.return_value = mock_response
        
        urls = self.scraper.get_all_listing_pages()
        self.assertIsInstance(urls, list)
        self.assertGreater(len(urls), 0)
    
    def test_parse_product_valid(self):
        """Test parsing valid product."""
        mock_div = MagicMock()
        mock_name = MagicMock()
        mock_name.text.strip.return_value = "iPhone 13 Pro"
        
        mock_div.select_one.side_effect = lambda selector: {
            "h3.sc-3ff391e0-4, h3.iwNALa": mock_name,
            "a[href]": MagicMock(get=lambda x: "/mobile-phone/iphone-13"),
            "span": MagicMock(text="999₾")
        }.get(selector)
        
        result = self.scraper.parse_product_from_listing(mock_div)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['name'], "iPhone 13 Pro")
        self.assertEqual(result['price'], 999)
    
    def test_parse_product_invalid(self):
        """Test parsing invalid product."""
        mock_div = MagicMock()
        mock_div.select_one.return_value = MagicMock(text="Unknown")
        
        result = self.scraper.parse_product_from_listing(mock_div)
        self.assertIsNone(result)
    
    @patch('requests.get')
    def test_parse_product_details(self, mock_get):
        """Test parsing product details."""
        mock_response = MagicMock()
        mock_response.content = '''
        <html><body>
            <span class="sc-235e453a-19 eOnNNp">SKU123</span>
            <li class="sc-235e453a-27 khePzm">Spec 1</li>
            <div class="sc-235e453a-24 hVytZX">
                <a>12 months warranty</a>
            </div>
        </body></html>
        '''
        mock_get.return_value = mock_response
        
        result = self.scraper.parse_product_details("https://beta.ee.ge/test")
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['sku'], "SKU123")
        self.assertIn("12 months warranty", result['warranty'])


if __name__ == '__main__':
    unittest.main() 