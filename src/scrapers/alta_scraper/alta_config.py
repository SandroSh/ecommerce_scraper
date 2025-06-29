import logging
from typing import Dict, Tuple


class AltaConfig:
    """Configuration class for Alta.ge scraper."""

    BASE_URL = "https://alta.ge"

    CATEGORY_URLS = {
        'phones': '/en/mobile-phones-accessories/mobile-phones-c16s',
        'laptops': '/en/computers-accessories-c2s',
        'tvs': '/en/tv-audio-c3s',
        'fridges': '/en/home-appliances-c6s'
    }

    # Selenium settings
    PAGE_LOAD_TIMEOUT = 45
    ELEMENT_TIMEOUT = 15
    DELAY_RANGE = (2, 5)

    # Enhanced Product selectors - more comprehensive coverage
    PRODUCT_SELECTORS = [
        # Primary selectors based on visible HTML structure
        'div[class*="sc-4a8e2816"]',  # Main product container
        'div[class*="sc-35fd0e08"]',  # Secondary product container
        'div[class*="sc-eee205a"]',  # Grid container items
        'div[class*="sc-88de82a8"]',  # Product detail containers

        # Additional dynamic selectors
        'div[class*="sc-"][class*="grid"]',
        'div[class*="sc-"][class*="item"]',
        'div[class*="sc-"][class*="card"]',

        # Fallback selectors
        '.product-card',
        '.product-item',
        '[class*="product"]',
        'div[class*="card"]',

        # Generic containers that might hold products
        'article',
        'div[data-testid*="product"]',
        'div[role="listitem"]'
    ]

    # Enhanced Name selectors
    NAME_SELECTORS = [
        # Primary name selectors
        'h2[class*="sc-4a8e2816"]',
        'h1[class*="sc-bf675a3"]',  # Seen in laptop section
        'h2[class*="sc-bf675a3"]',
        'a[class*="sc-4a8e2816"]',

        # Title attributes (often contain full product names)
        'a[title]',
        'h1[title]',
        'h2[title]',
        'span[title]',

        # Generic selectors
        '.product-title',
        '.item-title',
        '.product-name',

        # Heading tags
        'h1', 'h2', 'h3', 'h4',

        # Link text that might contain product names
        'a[href*="/laptop/"]',
        'a[href*="/tv/"]',
        'a[href*="/refrigerator/"]',
        'a[href*="/mobile-phones/"]'
    ]

    # Enhanced Price selectors
    PRICE_SELECTORS = [
        # Primary price selectors
        'span[class*="sc-88de82a8"]',
        'div[class*="sc-88de82a8"]',

        # Price-specific classes
        'span[class*="price"]',
        'div[class*="price"]',
        '.price',
        '.current-price',
        '.final-price',

        # Cost and amount selectors
        '[class*="cost"]',
        '[class*="amount"]',
        '[class*="currency"]',

        # Georgian currency specific
        'span:contains("₾")',
        'div:contains("₾")',
        'span:contains("ლ")',

        # Numeric patterns that might be prices
        'span[class*="sc-"]:contains("₾")',
        'div[class*="sc-"]:contains("₾")'
    ]

    # Enhanced Link selectors with category-specific patterns
    LINK_SELECTORS = [
        # Category-specific URL patterns
        'a[href*="/laptop/"]',
        'a[href*="/tv/"]',
        'a[href*="/television/"]',
        'a[href*="/refrigerator/"]',
        'a[href*="/mobile-phones/"]',
        'a[href*="/smartphone/"]',

        # Generic product links
        'a[href*="/product/"]',
        'a[href*="/item/"]',

        # Class-based selectors
        'a[class*="sc-4a8e2816"]',
        'a[class*="product"]',

        # Any link within product containers
        'a[href]'
    ]

    # Category-specific selectors for better targeting
    CATEGORY_SPECIFIC_SELECTORS = {
        'laptops': {
            'container': [
                'div[class*="sc-4a8e2816"]',
                'div[class*="sc-35fd0e08"]'
            ],
            'name': [
                'h2[class*="sc-bf675a3"]',
                'a[title*="VivoBook"]',
                'a[title*="IdeaPad"]',
                'a[title*="Laptop"]'
            ],
            'price': [
                'span[class*="sc-88de82a8"]',
                'div[class*="price"]'
            ]
        },
        'tvs': {
            'container': [
                'div[class*="sc-4a8e2816"]',
                'div[class*="sc-35fd0e08"]'
            ],
            'name': [
                'h2[class*="sc-bf675a3"]',
                'a[title*="TV"]',
                'a[title*="Smart"]',
                'a[title*="OLED"]',
                'a[title*="LED"]'
            ],
            'price': [
                'span[class*="sc-88de82a8"]'
            ]
        },
        'fridges': {
            'container': [
                'div[class*="sc-4a8e2816"]',
                'div[class*="sc-35fd0e08"]'
            ],
            'name': [
                'h2[class*="sc-bf675a3"]',
                'a[title*="Samsung"]',
                'a[title*="Refrigerator"]',
                'a[title*="Fridge"]'
            ],
            'price': [
                'span[class*="sc-88de82a8"]'
            ]
        },
        'phones': {
            'container': [
                'div[class*="sc-4a8e2816"]',
                'div[class*="sc-35fd0e08"]'
            ],
            'name': [
                'h2[class*="sc-4a8e2816"]',
                'a[class*="sc-4a8e2816"]'
            ],
            'price': [
                'span[class*="sc-88de82a8"]'
            ]
        }
    }

    # Brands expanded with more comprehensive list
    BRANDS = [
        # Mobile phone brands
        'Apple', 'Samsung', 'Xiaomi', 'Huawei', 'OnePlus', 'Sony', 'LG',
        'Google', 'Motorola', 'Nokia', 'Honor', 'Realme', 'Oppo', 'Vivo',
        'iPhone', 'Galaxy', 'Redmi', 'Mi', 'Pixel', 'Nothing', 'Fairphone',

        # Laptop brands
        'HP', 'Dell', 'Lenovo', 'Asus', 'Acer', 'MSI', 'MacBook', 'Apple',
        'Surface', 'ThinkPad', 'Pavilion', 'Inspiron', 'Predator', 'ROG',
        'VivoBook', 'IdeaPad', 'Yoga', 'Aspire', 'TravelMate', 'ZenBook',

        # TV brands
        'Samsung', 'LG', 'Sony', 'Panasonic', 'Philips', 'TCL', 'Hisense',
        'Sharp', 'Toshiba', 'Roku', 'Amazon', 'Fire TV', 'Android TV',
        'QLED', 'OLED', 'NanoCell', 'Crystal', 'Bravia',

        # Refrigerator brands
        'Samsung', 'LG', 'Bosch', 'Whirlpool', 'Electrolux', 'Indesit',
        'Hotpoint', 'Siemens', 'Miele', 'Candy', 'Beko', 'Zanussi',
        'AEG', 'Haier', 'Liebherr', 'Smeg', 'Gorenje', 'Atlant'
    ]

    # Chrome options
    CHROME_OPTIONS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-blink-features=AutomationControlled',
        '--window-size=1920,1080',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor'
    ]

    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

    @staticmethod
    def get_category_selectors(category: str) -> Dict[str, list]:
        """Get category-specific selectors."""
        return AltaConfig.CATEGORY_SPECIFIC_SELECTORS.get(category, {
            'container': AltaConfig.PRODUCT_SELECTORS,
            'name': AltaConfig.NAME_SELECTORS,
            'price': AltaConfig.PRICE_SELECTORS
        })

    @staticmethod
    def setup_logging(debug: bool = False) -> logging.Logger:
        """Setup logging configuration."""
        log_level = logging.DEBUG if debug else logging.INFO

        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)

        # Clear existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger