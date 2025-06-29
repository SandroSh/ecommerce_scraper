"""
Data handling utilities for scrapers
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import json
import csv
import os


@dataclass
class Product:
    """Simple product data structure without database dependencies"""
    name: str
    price: str
    brand: str
    category: str
    description: str
    url: str = ""
    sku: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
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
    """Save products to JSON file - handles both Product objects and dictionaries"""
    # Convert products to dictionaries
    data = []
    for product in products:
        if hasattr(product, 'to_dict'):
            # Product object
            data.append(product.to_dict())
        elif isinstance(product, dict):
            # Already a dictionary
            data.append(product)
        else:
            # Try to convert to dict if possible
            try:
                data.append(dict(product))
            except:
                # Fallback: convert to string representation
                data.append({"data": str(product)})
    
    # Ensure output directory exists
    os.makedirs("data_output", exist_ok=True)
    filepath = os.path.join("data_output", filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filepath


def save_products_to_csv(products: List[Product], filename: str = "products.csv"):
    """Save products to CSV file"""
    if not products:
        return None
    
    # Ensure output directory exists
    os.makedirs("data_output", exist_ok=True)
    filepath = os.path.join("data_output", filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=products[0].to_dict().keys())
        writer.writeheader()
        for product in products:
            writer.writerow(product.to_dict())
    
    return filepath


def extract_brand_from_name(name: str) -> str:
    """Extract brand from product name"""
    if not name:
        return "Unknown"
    
    # Common brand patterns
    brands = [
        "Apple", "Samsung", "Xiaomi", "Huawei", "OnePlus", "Google", "Sony", 
        "LG", "Nokia", "Motorola", "HTC", "BlackBerry", "Asus", "Lenovo",
        "Oppo", "Vivo", "Realme", "Nothing", "ZTE", "Alcatel"
    ]
    
    name_words = name.split()
    for word in name_words:
        if word in brands:
            return word
    
    # Return first word as brand if no known brand found
    return name_words[0] if name_words else "Unknown"


def clean_price(price_text: str) -> str:
    """Clean and standardize price text"""
    if not price_text:
        return "N/A"
    
    # Remove extra whitespace and common price prefixes
    cleaned = price_text.strip()
    
    # Keep only digits, decimal points, and currency symbols
    import re
    cleaned = re.sub(r'[^\d.,₾$€£¥\s]', '', cleaned)
    
    return cleaned.strip() if cleaned else "N/A" 