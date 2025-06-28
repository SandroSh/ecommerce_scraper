import json
import os
import logging
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from itemadapter import ItemAdapter
import hashlib


class ValidationPipeline:
    """Validate scraped items"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Validate required fields
        if not adapter.get('name'):
            self.logger.warning(f"Item missing name: {adapter.get('url')}")
            raise DropItem(f"Missing name: {item}")

        # Clean and validate price
        price = adapter.get('price')
        if price:
            try:
                # Remove non-numeric characters except dots and commas
                cleaned_price = ''.join(c for c in str(price) if c.isdigit() or c in '.,')
                adapter['price'] = cleaned_price
            except (ValueError, TypeError):
                adapter['price'] = None

        # Validate URL
        if not adapter.get('url'):
            raise DropItem(f"Missing URL: {item}")

        # Generate item ID based on URL
        item_id = hashlib.md5(adapter['url'].encode()).hexdigest()
        adapter['item_id'] = item_id

        return item


class RawDataPipeline:
    """Save raw scraped data to files"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.raw_data_dir = 'data_output/raw'
        self.processed_data_dir = 'data_output/processed'

        # Create directories if they don't exist
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)

        # Initialize files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.raw_file = os.path.join(self.raw_data_dir, f'raw_scraped_data_{timestamp}.jsonl')
        self.processed_file = os.path.join(self.processed_data_dir, f'processed_data_{timestamp}.json')

        self.processed_items = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Save raw data (including HTML)
        raw_item = dict(adapter)

        with open(self.raw_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(raw_item, ensure_ascii=False, default=str) + '\n')

        # Prepare processed item (without raw HTML)
        processed_item = {
            'item_id': raw_item.get('item_id'),
            'name': raw_item.get('name'),
            'price': raw_item.get('price'),
            'brand': raw_item.get('brand'),
            'category': raw_item.get('category'),
            'description': raw_item.get('description'),
            'images': raw_item.get('images', []),
            'specifications': raw_item.get('specifications', {}),
            'availability': raw_item.get('availability'),
            'rating': raw_item.get('rating'),
            'url': raw_item.get('url'),
            'scraped_at': raw_item.get('scraped_at')
        }

        self.processed_items.append(processed_item)

        return item

    def close_spider(self, spider):
        # Save processed data
        with open(self.processed_file, 'w', encoding='utf-8') as f:
            json.dump(self.processed_items, f, ensure_ascii=False, indent=2, default=str)

        self.logger.info(f"Saved {len(self.processed_items)} processed items to {self.processed_file}")


class DatabasePipeline:
    """Save processed data to database"""

    def __init__(self, database_url):
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        database_url = crawler.settings.get("DATABASE_URL")
        return cls(database_url)

    def open_spider(self, spider):
        try:
            self.engine = create_engine(self.database_url)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            self.engine = None

    def process_item(self, item, spider):
        if not self.engine:
            return item

        try:
            session = self.Session()
            adapter = ItemAdapter(item)

            # Import here to avoid circular imports
            from src.data.models import Product

            # Check if item already exists
            existing_item = session.query(Product).filter_by(
                name=adapter.get('name'),
                brand=adapter.get('brand')
            ).first()

            if existing_item:
                # Update existing item
                existing_item.price = adapter.get('price')
                existing_item.description = adapter.get('description')
                existing_item.created_at = datetime.now()
            else:
                # Create new item
                product = Product(
                    name=adapter.get('name'),
                    price=adapter.get('price'),
                    brand=adapter.get('brand'),
                    category=adapter.get('category'),
                    description=adapter.get('description')
                )
                session.add(product)

            session.commit()
            session.close()

        except Exception as e:
            self.logger.error(f"Error saving item to database: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()

        return item

    def close_spider(self, spider):
        if hasattr(self, 'engine') and self.engine:
            self.engine.dispose()


class DuplicatesPipeline:
    """Filter out duplicate items"""

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        item_id = adapter.get('item_id')

        if item_id in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item_id}")
        else:
            self.ids_seen.add(item_id)
            return item


from scrapy.exceptions import DropItem