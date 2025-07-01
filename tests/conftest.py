"""
Pytest configuration and common fixtures.

This module provides common test fixtures and configuration for the test suite.
"""

import pytest
import tempfile
import os
import pandas as pd
from datetime import datetime, timedelta


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    import shutil
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_products():
    """Sample product data for testing."""
    return [
        {
            'name': 'iPhone 13 Pro',
            'price': 999,
            'brand': 'Apple',
            'category': 'phones',
            'description': 'Latest iPhone model',
            'url': 'https://example.com/iphone',
            'sku': 'IPHONE13PRO',
            'timestamp': datetime.now().isoformat()
        },
        {
            'name': 'Samsung Galaxy S21',
            'price': 799,
            'brand': 'Samsung',
            'category': 'phones',
            'description': 'Android flagship',
            'url': 'https://example.com/samsung',
            'sku': 'SAMSUNGS21',
            'timestamp': datetime.now().isoformat()
        },
        {
            'name': 'Xiaomi Mi 11',
            'price': 599,
            'brand': 'Xiaomi',
            'category': 'phones',
            'description': 'Budget flagship',
            'url': 'https://example.com/xiaomi',
            'sku': 'XIAOMIMI11',
            'timestamp': datetime.now().isoformat()
        }
    ]


@pytest.fixture
def sample_dataframe():
    """Sample pandas DataFrame for testing."""
    return pd.DataFrame({
        'name': ['iPhone 13', 'Samsung Galaxy', 'Xiaomi Mi 11', 'iPhone 12', 'Samsung Note'],
        'price': [999, 799, 599, 899, 899],
        'brand': ['Apple', 'Samsung', 'Xiaomi', 'Apple', 'Samsung'],
        'category': ['phones', 'phones', 'phones', 'phones', 'phones'],
        'description': ['Latest iPhone', 'Android flagship', 'Budget phone', 'Previous iPhone', 'Note series'],
        'source': ['ee.ge', 'ee.ge', 'ee.ge', 'ee.ge', 'ee.ge'],
        'createdat': [
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=3),
            datetime.now() - timedelta(days=4),
            datetime.now() - timedelta(days=5)
        ]
    })


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    import logging
    from unittest.mock import MagicMock
    
    mock_logger = MagicMock(spec=logging.Logger)
    mock_logger.info = MagicMock()
    mock_logger.warning = MagicMock()
    mock_logger.error = MagicMock()
    mock_logger.debug = MagicMock()
    
    return mock_logger


@pytest.fixture
def sample_html_content():
    """Sample HTML content for testing scrapers."""
    return '''
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <div class="product">
                <h3 class="sc-3ff391e0-4">iPhone 13 Pro</h3>
                <a href="/mobile-phone/iphone-13-pro" class="sc-3ff391e0-3">View Details</a>
                <span class="sc-3ff391e0-6">999₾</span>
            </div>
            <div class="product">
                <h3 class="sc-3ff391e0-4">Samsung Galaxy S21</h3>
                <a href="/mobile-phone/samsung-galaxy-s21" class="sc-3ff391e0-3">View Details</a>
                <span class="sc-3ff391e0-6">799₾</span>
            </div>
            <div class="pagination">
                <a href="?page=1">Page 1</a>
                <a href="?page=2">Page 2</a>
                <a href="?page=3">Page 3</a>
            </div>
        </body>
    </html>
    '''


@pytest.fixture
def sample_product_html():
    """Sample product detail HTML content."""
    return '''
    <html>
        <head>
            <title>iPhone 13 Pro - Product Details</title>
        </head>
        <body>
            <span class="sc-235e453a-19 eOnNNp">IPHONE13PRO</span>
            <ul>
                <li class="sc-235e453a-27 khePzm">6.1-inch Super Retina XDR display</li>
                <li class="sc-235e453a-27 khePzm">A15 Bionic chip</li>
                <li class="sc-235e453a-27 khePzm">Pro camera system</li>
            </ul>
            <div class="sc-235e453a-24 hVytZX">
                <a>12 months warranty</a>
                <a>Free shipping</a>
            </div>
            <table class="sc-bc705976-4 bbQIJZ">
                <tr class="sc-bc705976-6 UicTo">
                    <td class="sc-bc705976-7">Storage</td>
                    <td class="sc-bc705976-7">128GB</td>
                </tr>
                <tr class="sc-bc705976-6 UicTo">
                    <td class="sc-bc705976-7">Color</td>
                    <td class="sc-bc705976-7">Sierra Blue</td>
                </tr>
            </table>
        </body>
    </html>
    ''' 