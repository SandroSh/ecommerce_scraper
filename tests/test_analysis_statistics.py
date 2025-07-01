"""
Unit tests for statistics analysis module.
"""

import unittest
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.analysis.statistics import StatisticalAnalyzer


class TestStatisticalAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'name': ['iPhone 13', 'Samsung Galaxy', 'Xiaomi Mi 11'],
            'price': [999, 799, 599],
            'brand': ['Apple', 'Samsung', 'Xiaomi'],
            'category': ['phones', 'phones', 'phones'],
            'source': ['ee.ge', 'ee.ge', 'ee.ge'],
            'createdat': [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=3)
            ]
        })
        self.analyzer = StatisticalAnalyzer(self.sample_data)
    
    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertEqual(len(self.analyzer.data), 3)
        self.assertIsNotNone(self.analyzer.logger)
    
    def test_descriptive_statistics(self):
        """Test descriptive statistics generation."""
        stats = self.analyzer.descriptive_statistics()
        
        self.assertEqual(stats['overview']['total_records'], 3)
        self.assertEqual(stats['price_statistics']['mean'], 799.0)
        self.assertEqual(stats['price_statistics']['count'], 3)
    
    def test_brand_analysis(self):
        """Test brand analysis."""
        analysis = self.analyzer.brand_analysis()
        market_share = analysis['market_share']
        
        self.assertEqual(market_share['Apple']['count'], 1)
        self.assertEqual(market_share['Samsung']['count'], 1)
        self.assertEqual(market_share['Xiaomi']['count'], 1)
    
    @patch('scipy.stats.shapiro')
    @patch('scipy.stats.kstest')
    def test_price_distribution(self, mock_kstest, mock_shapiro):
        """Test price distribution analysis."""
        mock_shapiro.return_value = (0.95, 0.1)
        mock_kstest.return_value = (0.1, 0.2)
        
        analysis = self.analyzer.price_distribution_analysis()
        
        self.assertIn('distribution_tests', analysis)
        self.assertIn('outliers', analysis)
        self.assertIn('price_segments', analysis)
    
    def test_empty_data(self):
        """Test with empty dataframe."""
        empty_data = pd.DataFrame(columns=self.sample_data.columns)
        analyzer = StatisticalAnalyzer(empty_data)
        
        stats = analyzer.descriptive_statistics()
        self.assertEqual(stats['overview']['total_records'], 0)


if __name__ == '__main__':
    unittest.main() 