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
    # Updated product container selectors
    PRODUCT_SELECTORS = [
        'div[class*="sc-"][class*="gBOJXd"]',  # Main product containers
        'div[class*="sc-28c9b3a8-"]',  # Product card containers
        'div[class*="sc-4cc3966f-"]',  # Category containers
        'div[class*="sc-88de82a8-"]',  # Individual product items
        'article[class*="sc-"]',  # Article containers
        '.product-item',  # Fallback
        '.product-card',  # Fallback
    ]

    # Updated name selectors
    NAME_SELECTORS = [
        'h2[class*="sc-"][class*="kfQwkI"]',  # Product titles
        'h1[class*="sc-"][class*="dyUwJu"]',  # Main product names
        'h2[title]',  # Elements with title attribute
        'a[title]',  # Links with titles
        '[class*="sc-28c9b3a8-"] h2',  # Headers in product cards
        '[class*="sc-bf675a3-"] h1',  # Product detail titles
    ]

    # Updated price selectors
    PRICE_SELECTORS = [
        'span[class*="currency"]',  # Currency spans
        'span[class*="sc-28c9b3a8-"][class*="jkcOBV"]',  # Price elements
        'div[class*="sc-88de82a8-"] span',  # Price in product containers
        '[class*="price"]',  # Generic price classes
        'span:contains("₾")',  # Georgian Lari symbol
        'span:contains("ლ")',  # Alternative currency
    ]

    # Updated image selectors
    IMAGE_SELECTORS = [
        'img[class*="sc-28c9b3a8-"]',  # Product images
        'img[data-nimg="fill"]',  # Next.js images
        'img[decoding="async"]',  # Async loaded images
        'img[src*="imagestore.alta.ge"]',  # Alta's image CDN
    ]

    # Category-specific selectors
    CATEGORY_SELECTORS = {
        'phones': {
            'container': [
                'div[class*="sc-28c9b3a8-0"]',
                'div[class*="iuDoCo"]',
                'a[href*="/mobile-phones/"]',
            ],
            'name': [
                'h2[class*="sc-28c9b3a8-10"]',
                'h1[class*="sc-bf675a3-2"]',
                'h2[title*="Samsung"]',
                'h2[title*="iPhone"]',
                'h2[title*="Realme"]',
            ],
            'price': [
                'span[class*="sc-28c9b3a8-13"]',
                'span[class*="jkcOBV"]',
                'span[class*="currency"]',
            ]
        }
    }

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