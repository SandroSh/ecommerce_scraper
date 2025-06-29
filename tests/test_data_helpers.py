"""
Unit tests for data helpers module.
"""

import unittest
import tempfile
import os
import json
import pandas as pd
from unittest.mock import patch, mock_open

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.data_helpers import (
    Product, save_products_to_json, save_products_to_csv,
    extract_brand_from_name, clean_price
)


class TestDataHelpers(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_products = [
            Product("iPhone 13", "999", "Apple", "phones", "Smartphone"),
            Product("Samsung Galaxy", "799", "Samsung", "phones", "Android phone")
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_product_creation(self):
        """Test Product object creation."""
        product = Product("iPhone 13", "999", "Apple", "phones", "Smartphone")
        
        self.assertEqual(product.name, "iPhone 13")
        self.assertEqual(product.price, "999")
        self.assertEqual(product.brand, "Apple")
        self.assertIsNotNone(product.created_at)
    
    def test_save_json(self):
        """Test saving products to JSON."""
        filepath = os.path.join(self.temp_dir, "test_products.json")
        
        result = save_products_to_json(self.test_products, filepath)
        self.assertEqual(result, filepath)
        self.assertTrue(os.path.exists(filepath))
    
    def test_extract_brand(self):
        """Test brand extraction from product names."""
        self.assertEqual(extract_brand_from_name("iPhone 13 Pro"), "Apple")
        self.assertEqual(extract_brand_from_name("Samsung Galaxy S21"), "Samsung")
        self.assertEqual(extract_brand_from_name("Unknown Phone"), "Unknown")
    
    def test_clean_price(self):
        """Test price cleaning."""
        self.assertEqual(clean_price("999₾"), "999₾")
        self.assertEqual(clean_price("$999.99"), "999.99")
        self.assertEqual(clean_price(""), "N/A")
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_with_mock(self, mock_file):
        """Test saving with mocked file."""
        filepath = "/test/path/products.json"
        result = save_products_to_json(self.test_products, filepath)
        
        self.assertEqual(result, filepath)
        mock_file.assert_called_once_with(filepath, 'w', encoding='utf-8')


if __name__ == '__main__':
    unittest.main() 