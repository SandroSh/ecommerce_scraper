"""
Integration tests for the ecommerce scraper project.

Tests cover the integration between different modules and components:
- Data flow from scrapers to data helpers
- Analysis pipeline integration
- End-to-end workflows
"""

import unittest
import tempfile
import os
import json
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.data_helpers import Product, save_products_to_json, extract_brand_from_name
from src.utils.logger import get_logger
from src.analysis.statistics import StatisticalAnalyzer


class TestDataFlowIntegration(unittest.TestCase):
    """Test integration of data flow between modules."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_products = [
            Product("iPhone 13 Pro", "999", "Apple", "phones", "Latest iPhone"),
            Product("Samsung Galaxy S21", "799", "Samsung", "phones", "Android flagship"),
            Product("Xiaomi Mi 11", "599", "Xiaomi", "phones", "Budget flagship")
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_scraper_to_data_helpers_integration(self):
        """Test integration between scraper output and data helpers."""
        # Simulate scraper output (dictionaries)
        scraper_output = [
            {
                'name': 'iPhone 13 Pro',
                'price': 999,
                'brand': 'Apple',
                'category': 'phones',
                'description': 'Latest iPhone model',
                'link': 'https://example.com/iphone',
                'source': 'ee.ge',
                'timestamp': datetime.now().isoformat()
            },
            {
                'name': 'Samsung Galaxy S21',
                'price': 799,
                'brand': 'Samsung',
                'category': 'phones',
                'description': 'Android flagship',
                'link': 'https://example.com/samsung',
                'source': 'ee.ge',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        # Test that data helpers can process scraper output
        json_file = save_products_to_json(scraper_output, "integration_test.json")
        
        # Verify file was created
        self.assertTrue(os.path.exists(json_file))
        
        # Load and verify data
        with open(json_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]['name'], 'iPhone 13 Pro')
        self.assertEqual(loaded_data[0]['brand'], 'Apple')
        self.assertEqual(loaded_data[1]['name'], 'Samsung Galaxy S21')
        self.assertEqual(loaded_data[1]['brand'], 'Samsung')
    
    def test_data_helpers_to_analysis_integration(self):
        """Test integration between data helpers and analysis modules."""
        # Create Product objects
        products = [
            Product("iPhone 13 Pro", "999", "Apple", "phones", "Latest iPhone"),
            Product("Samsung Galaxy S21", "799", "Samsung", "phones", "Android flagship"),
            Product("Xiaomi Mi 11", "599", "Xiaomi", "phones", "Budget flagship")
        ]
        
        # Convert to DataFrame for analysis
        data = []
        for product in products:
            data.append({
                'name': product.name,
                'price': float(product.price),
                'brand': product.brand,
                'category': product.category,
                'description': product.description,
                'source': 'ee.ge',
                'createdat': datetime.now()
            })
        
        df = pd.DataFrame(data)
        
        # Test analysis integration
        analyzer = StatisticalAnalyzer(df)
        stats = analyzer.descriptive_statistics()
        
        # Verify analysis results
        self.assertEqual(stats['overview']['total_records'], 3)
        self.assertEqual(stats['price_statistics']['mean'], 799.0)
        self.assertEqual(stats['price_statistics']['count'], 3)
        
        # Check brand analysis
        brand_analysis = analyzer.brand_analysis()
        self.assertEqual(brand_analysis['market_share']['Apple']['count'], 1)
        self.assertEqual(brand_analysis['market_share']['Samsung']['count'], 1)
        self.assertEqual(brand_analysis['market_share']['Xiaomi']['count'], 1)
    
    def test_logger_integration(self):
        """Test logger integration with other modules."""
        # Test logger with data helpers
        logger = get_logger("integration_test")
        
        # Test that logger works with data processing
        products = [
            Product("Test Product", "100", "Test Brand", "test", "Test description")
        ]
        
        # This should not raise any exceptions
        try:
            json_file = save_products_to_json(products, "logger_test.json")
            logger.info(f"Successfully saved {len(products)} products to {json_file}")
        except Exception as e:
            self.fail(f"Logger integration failed: {e}")
    
    def test_brand_extraction_integration(self):
        """Test brand extraction integration with product data."""
        # Test brand extraction with various product names
        test_cases = [
            ("iPhone 13 Pro Max", "Apple"),
            ("Samsung Galaxy S21 Ultra", "Samsung"),
            ("Xiaomi Mi 11 Ultra", "Xiaomi"),
            ("OnePlus 9 Pro", "OnePlus"),
            ("Google Pixel 6 Pro", "Google")
        ]
        
        for product_name, expected_brand in test_cases:
            with self.subTest(product_name=product_name):
                extracted_brand = extract_brand_from_name(product_name)
                self.assertEqual(extracted_brand, expected_brand)
                
                # Test integration with Product creation
                product = Product(
                    name=product_name,
                    price="999",
                    brand=extracted_brand,
                    category="phones",
                    description="Test product"
                )
                
                self.assertEqual(product.brand, expected_brand)
    
    def test_end_to_end_data_pipeline(self):
        """Test complete end-to-end data pipeline."""
        # Step 1: Create sample scraper data
        scraper_data = [
            {
                'name': 'iPhone 13 Pro',
                'price': 999,
                'brand': 'Apple',
                'category': 'phones',
                'description': 'Latest iPhone model',
                'link': 'https://example.com/iphone',
                'source': 'ee.ge',
                'timestamp': datetime.now().isoformat()
            },
            {
                'name': 'Samsung Galaxy S21',
                'price': 799,
                'brand': 'Samsung',
                'category': 'phones',
                'description': 'Android flagship',
                'link': 'https://example.com/samsung',
                'source': 'ee.ge',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        # Step 2: Save to JSON using data helpers
        json_file = save_products_to_json(scraper_data, "pipeline_test.json")
        
        # Step 3: Load data for analysis
        with open(json_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        # Step 4: Convert to DataFrame for analysis
        df = pd.DataFrame(loaded_data)
        df['createdat'] = pd.to_datetime(df['timestamp'])
        
        # Step 5: Perform analysis
        analyzer = StatisticalAnalyzer(df)
        stats = analyzer.descriptive_statistics()
        brand_analysis = analyzer.brand_analysis()
        
        # Step 6: Verify results
        self.assertEqual(stats['overview']['total_records'], 2)
        self.assertEqual(stats['price_statistics']['mean'], 899.0)
        self.assertEqual(len(brand_analysis['market_share']), 2)
        
        # Step 7: Test logging integration
        logger = get_logger("pipeline_test")
        logger.info(f"Pipeline completed: {stats['overview']['total_records']} products analyzed")
    
    def test_error_handling_integration(self):
        """Test error handling integration across modules."""
        # Test with invalid data
        invalid_products = [
            {
                'name': '',  # Invalid empty name
                'price': 'invalid',  # Invalid price
                'brand': '',  # Invalid empty brand
                'category': 'phones',
                'description': 'Test product',
                'source': 'ee.ge',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        # This should handle errors gracefully
        try:
            json_file = save_products_to_json(invalid_products, "error_test.json")
            
            # Load and analyze
            with open(json_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            df = pd.DataFrame(loaded_data)
            analyzer = StatisticalAnalyzer(df)
            stats = analyzer.descriptive_statistics()
            
            # Should still work with invalid data
            self.assertIn('overview', stats)
            self.assertIn('text_statistics', stats)
            
        except Exception as e:
            self.fail(f"Error handling integration failed: {e}")
    
    def test_performance_integration(self):
        """Test performance integration with larger datasets."""
        # Create larger dataset
        large_dataset = []
        for i in range(100):
            large_dataset.append({
                'name': f'Product {i}',
                'price': 100 + i,
                'brand': f'Brand {i % 5}',
                'category': 'phones',
                'description': f'Description for product {i}',
                'source': 'ee.ge',
                'timestamp': datetime.now().isoformat()
            })
        
        # Test performance of data helpers
        start_time = datetime.now()
        json_file = save_products_to_json(large_dataset, "performance_test.json")
        save_time = (datetime.now() - start_time).total_seconds()
        
        # Should complete within reasonable time
        self.assertLess(save_time, 5.0)  # Less than 5 seconds
        
        # Test performance of analysis
        with open(json_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        df = pd.DataFrame(loaded_data)
        df['createdat'] = pd.to_datetime(df['timestamp'])
        
        start_time = datetime.now()
        analyzer = StatisticalAnalyzer(df)
        stats = analyzer.descriptive_statistics()
        analysis_time = (datetime.now() - start_time).total_seconds()
        
        # Should complete within reasonable time
        self.assertLess(analysis_time, 10.0)  # Less than 10 seconds
        
        # Verify results
        self.assertEqual(stats['overview']['total_records'], 100)
        self.assertEqual(len(stats['overview']['brands']), 5)


if __name__ == '__main__':
    unittest.main() 