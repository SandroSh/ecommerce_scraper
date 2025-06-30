"""
Data Handling Utilities Module

This module provides comprehensive data handling utilities for the ecommerce scraper project.
It includes data structures, serialization functions, and data processing utilities
for managing product information across different output formats.

The module provides:
- Product data structure definition
- JSON and CSV export functionality
- Brand extraction utilities
- Price cleaning and standardization
- Data validation and transformation

All functions are designed to handle both Product objects and raw dictionaries,
providing flexibility for different data sources and formats.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import json
import csv
import os


@dataclass
class Product:
    """
    Data structure for representing product information.
    
    This dataclass provides a standardized way to store product data
    without database dependencies. It includes all essential product
    information and provides serialization methods for export.
    
    Attributes:
        name (str): Product name/title
        price (str): Product price (as string to handle various formats)
        brand (str): Product brand/manufacturer
        category (str): Product category (e.g., 'phones', 'accessories')
        description (str): Product description or additional details
        url (str): Product URL. Defaults to empty string.
        sku (str): Stock keeping unit. Defaults to empty string.
        created_at (Optional[datetime]): Timestamp of creation. Auto-generated if None.
    """
    
    name: str
    price: str
    brand: str
    category: str
    description: str
    url: str = ""
    sku: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize created_at timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self):
        """
        Convert the Product instance to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the product with all attributes.
        """
        return {
            'name': self.name,
            'price': self.price,
            'brand': self.brand,
            'category': self.category,
            'description': self.description,
            'url': self.url,
            'sku': self.sku,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def save_products_to_json(products: List, filename: str = "products.json"):
    """
    Save a list of products to a JSON file.
    
    This function handles both Product objects and raw dictionaries,
    automatically converting them to the appropriate format for JSON
    serialization. It creates the output directory if it doesn't exist.
    
    Args:
        products (List): List of products to save. Can contain Product objects
                        or dictionaries.
        filename (str): Name of the output JSON file. Defaults to "products.json".
    
    Returns:
        str: Full path to the created JSON file.
    """
    data = []
    for product in products:
        if hasattr(product, 'to_dict'):
            data.append(product.to_dict())
        elif isinstance(product, dict):
            data.append(product)
        else:
            try:
                data.append(dict(product))
            except:
                data.append({"data": str(product)})
    
    os.makedirs("data_output", exist_ok=True)
    filepath = os.path.join("data_output", filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filepath


def save_products_to_csv(products: List[Product], filename: str = "products.csv"):
    """
    Save a list of Product objects to a CSV file.
    
    This function creates a CSV file with headers based on the Product
    dataclass fields and writes all products to the file. It creates
    the output directory if it doesn't exist.
    
    Args:
        products (List[Product]): List of Product objects to save.
        filename (str): Name of the output CSV file. Defaults to "products.csv".
    
    Returns:
        str: Full path to the created CSV file, or None if no products provided.
    """
    if not products:
        return None
    
    os.makedirs("data_output", exist_ok=True)
    filepath = os.path.join("data_output", filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=products[0].to_dict().keys())
        writer.writeheader()
        for product in products:
            writer.writerow(product.to_dict())
    
    return filepath


def extract_brand_from_name(name: str) -> str:
    """
    Extract brand information from a product name.
    
    This function analyzes a product name to identify the brand by matching
    against a predefined list of known mobile phone brands. If no known brand
    is found, it returns the first word of the name as the brand.
    
    Args:
        name (str): Product name to analyze for brand information.
    
    Returns:
        str: Extracted brand name, or "Unknown" if no brand can be determined.
    """
    if not name:
        return "Unknown"
    
    brands = [
        "Apple", "Samsung", "Xiaomi", "Huawei", "OnePlus", "Google", "Sony", 
        "LG", "Nokia", "Motorola", "HTC", "BlackBerry", "Asus", "Lenovo",
        "Oppo", "Vivo", "Realme", "Nothing", "ZTE", "Alcatel"
    ]
    
    name_words = name.split()
    for word in name_words:
        if word in brands:
            return word
    
    return name_words[0] if name_words else "Unknown"


def clean_price(price_text: str) -> str:
    """
    Clean and standardize price text by removing unwanted characters.
    
    This function removes extra whitespace and non-numeric characters
    from price text while preserving digits, decimal points, and common
    currency symbols.
    
    Args:
        price_text (str): Raw price text to clean.
    
    Returns:
        str: Cleaned price text, or "N/A" if the input is empty or invalid.
    """
    if not price_text:
        return "N/A"
    
    cleaned = price_text.strip()
    
    import re
    cleaned = re.sub(r'[^\d.,₾$€£¥\s]', '', cleaned)
    
    return cleaned.strip() if cleaned else "N/A" 