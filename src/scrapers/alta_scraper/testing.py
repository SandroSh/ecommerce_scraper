#!/usr/bin/env python3
"""
Comprehensive testing script for Alta.ge scraper with config validation
and detailed scraping tests for all categories.
"""

import argparse
import time
import json
from pathlib import Path
from alta_selenium_scraper import AltaScraper
from alta_config import AltaConfig  # Import the config class


def validate_config():
    """Validate the AltaConfig class structure and content."""
    print("\n🔍 VALIDATING CONFIGURATION...")

    required_attributes = [
        'BASE_URL',
        'CATEGORY_URLS',
        'PAGE_LOAD_TIMEOUT',
        'ELEMENT_TIMEOUT',
        'DELAY_RANGE',
        'PRODUCT_SELECTORS',
        'NAME_SELECTORS',
        'PRICE_SELECTORS',
        'LINK_SELECTORS',
        'CATEGORY_SPECIFIC_SELECTORS',
        'BRANDS',
        'CHROME_OPTIONS',
        'USER_AGENT'
    ]

    missing_attributes = []
    for attr in required_attributes:
        if not hasattr(AltaConfig, attr):
            missing_attributes.append(attr)

    if missing_attributes:
        print(f"❌ Missing required attributes: {', '.join(missing_attributes)}")
        return False

    print("✅ All required configuration attributes present")

    # Validate category URLs
    expected_categories = ['phones', 'laptops', 'tvs', 'fridges']
    for category in expected_categories:
        if category not in AltaConfig.CATEGORY_URLS:
            print(f"❌ Missing URL for category: {category}")
            return False

    print("✅ All expected category URLs present")

    # Validate selectors are not empty
    selector_attributes = [
        'PRODUCT_SELECTORS',
        'NAME_SELECTORS',
        'PRICE_SELECTORS',
        'LINK_SELECTORS'
    ]

    for attr in selector_attributes:
        if not getattr(AltaConfig, attr):
            print(f"❌ Empty selector list: {attr}")
            return False

    print("✅ All selector lists contain values")

    # Validate category-specific selectors
    for category in expected_categories:
        if category not in AltaConfig.CATEGORY_SPECIFIC_SELECTORS:
            print(f"❌ Missing category-specific selectors for: {category}")
            return False

        cat_selectors = AltaConfig.CATEGORY_SPECIFIC_SELECTORS[category]
        if not all(key in cat_selectors for key in ['container', 'name', 'price']):
            print(f"❌ Incomplete selectors for category: {category}")
            return False

    print("✅ All category-specific selectors are complete")

    return True


def test_config_methods():
    """Test the methods in the AltaConfig class."""
    print("\n🧪 TESTING CONFIG METHODS...")

    # Test get_category_selectors
    try:
        for category in AltaConfig.CATEGORY_URLS.keys():
            selectors = AltaConfig.get_category_selectors(category)
            if not all(key in selectors for key in ['container', 'name', 'price']):
                print(f"❌ get_category_selectors failed for {category}")
                return False

        print("✅ get_category_selectors works for all categories")

        # Test with invalid category
        invalid_selectors = AltaConfig.get_category_selectors('invalid_category')
        if (invalid_selectors['container'] != AltaConfig.PRODUCT_SELECTORS or
                invalid_selectors['name'] != AltaConfig.NAME_SELECTORS or
                invalid_selectors['price'] != AltaConfig.PRICE_SELECTORS):
            print("❌ get_category_selectors failed for invalid category")
            return False

        print("✅ get_category_selectors handles invalid categories correctly")

    except Exception as e:
        print(f"❌ get_category_selectors test failed: {str(e)}")
        return False

    # Test setup_logging
    try:
        logger = AltaConfig.setup_logging(debug=False)
        if not isinstance(logger, logging.Logger):
            print("❌ setup_logging didn't return a Logger instance")
            return False

        debug_logger = AltaConfig.setup_logging(debug=True)
        if debug_logger.level != logging.DEBUG:
            print("❌ setup_logging didn't set DEBUG level correctly")
            return False

        print("✅ setup_logging works correctly")

    except Exception as e:
        print(f"❌ setup_logging test failed: {str(e)}")
        return False

    return True


def scrape_single_category(category: str, max_products: int, headless: bool, debug: bool):
    """Scrape a single category and return detailed results."""
    print(f"\n{'=' * 60}")
    print(f"🚀 STARTING SCRAPE FOR CATEGORY: {category.upper()}")
    print(f"{'=' * 60}")

    # Display config being used for this category
    print("\n⚙️ CONFIGURATION FOR THIS CATEGORY:")
    print(f"URL: {AltaConfig.BASE_URL}{AltaConfig.CATEGORY_URLS[category]}")
    selectors = AltaConfig.get_category_selectors(category)
    print(f"Container selectors: {selectors['container'][:2]}... ({len(selectors['container'])} total)")
    print(f"Name selectors: {selectors['name'][:2]}... ({len(selectors['name'])} total)")
    print(f"Price selectors: {selectors['price'][:2]}... ({len(selectors['price'])} total)")

    scraper = AltaScraper(
        headless=headless,
        max_products=max_products,
        debug=debug
    )

    try:
        start_time = time.time()
        output_file = scraper.run(category)
        elapsed_time = time.time() - start_time

        # Verify the output file
        if output_file and Path(output_file).exists():
            with open(output_file, 'r') as f:
                data = json.load(f)
                product_count = len(data)

            return {
                'category': category,
                'success': True,
                'output_file': output_file,
                'product_count': product_count,
                'time_elapsed': f"{elapsed_time:.2f} seconds",
                'error': None
            }
        else:
            return {
                'category': category,
                'success': False,
                'output_file': None,
                'product_count': 0,
                'time_elapsed': f"{elapsed_time:.2f} seconds",
                'error': "No output file was created"
            }

    except Exception as e:
        return {
            'category': category,
            'success': False,
            'output_file': None,
            'product_count': 0,
            'time_elapsed': 0,
            'error': str(e)
        }


def print_detailed_summary(results: list):
    """Print a detailed summary of all scraping results."""
    print(f"\n{'=' * 80}")
    print(f"📊 DETAILED SCRAPING SUMMARY")
    print(f"{'=' * 80}")

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"\n📌 OVERVIEW:")
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")

    if successful:
        print(f"\n🏆 SUCCESSFUL SCRAPES:")
        for result in successful:
            print(f"\n   📦 {result['category'].upper()}")
            print(f"      📁 File: {result['output_file']}")
            print(f"      🔢 Products: {result['product_count']}")
            print(f"      ⏱️  Time: {result['time_elapsed']}")

            # Show first product details if available
            try:
                with open(result['output_file'], 'r') as f:
                    products = json.load(f)
                    if products:
                        first_product = products[0]
                        print(f"\n      🛒 SAMPLE PRODUCT:")
                        print(f"         Name: {first_product.get('name', 'N/A')[:60]}...")
                        print(f"         Price: {first_product.get('price', 'N/A')}")
                        print(f"         URL: {first_product.get('url', 'N/A')[:80]}...")
            except Exception as e:
                print(f"      ⚠️ Couldn't read sample product: {str(e)}")

    if failed:
        print(f"\n💥 FAILED SCRAPES:")
        for result in failed:
            print(f"\n   ❌ {result['category'].upper()}")
            print(f"      ⏱️  Time: {result['time_elapsed']}")
            print(f"      🐞 Error: {result['error']}")

            # Special handling for common errors
            if "timeout" in result['error'].lower():
                print("      💡 Suggestion: Try increasing timeout in AltaConfig")
            elif "selector" in result['error'].lower():
                print("      💡 Suggestion: Check your CSS selectors in AltaConfig")


def main():
    """Enhanced main method with config validation and detailed testing."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Alta.ge Scraper Test Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate configuration only:
  python testing.py --validate-only

  # Test all categories with validation:
  python testing.py --all --validate

  # Test specific categories with debug:
  python testing.py --categories phones laptops --debug

  # Performance test with many products:
  python testing.py --all --max-products 100 --headless
        """
    )

    # Category selection options
    category_group = parser.add_mutually_exclusive_group(required=False)
    category_group.add_argument('--category', '-c',
                                choices=['phones', 'laptops', 'tvs', 'fridges'],
                                help='Single product category to test')
    category_group.add_argument('--categories',
                                choices=['phones', 'laptops', 'tvs', 'fridges'],
                                nargs='+',
                                help='Multiple categories to test')
    category_group.add_argument('--all', '-a',
                                action='store_true',
                                help='Test all available categories')
    category_group.add_argument('--validate-only',
                                action='store_true',
                                help='Only validate configuration without scraping')

    # Testing options
    parser.add_argument('--max-products', '-m',
                        type=int, default=20,
                        help='Maximum number of products to scrape per category')
    parser.add_argument('--headless',
                        action='store_true',
                        help='Run browser in headless mode')
    parser.add_argument('--debug', '-d',
                        action='store_true',
                        help='Enable debug mode with detailed logging')
    parser.add_argument('--delay',
                        type=int, default=10,
                        help='Delay in seconds between categories')
    parser.add_argument('--validate',
                        action='store_true',
                        help='Validate configuration before scraping')

    args = parser.parse_args()

    # Configuration validation
    if args.validate or args.validate_only:
        if not validate_config():
            print("\n❌ CONFIGURATION VALIDATION FAILED")
            return

        if not test_config_methods():
            print("\n❌ CONFIGURATION METHOD TESTS FAILED")
            return

        print("\n🎉 ALL CONFIGURATION TESTS PASSED")

        if args.validate_only:
            return

    # Determine which categories to test
    if args.all:
        categories_to_test = list(AltaConfig.CATEGORY_URLS.keys())
    elif args.categories:
        categories_to_test = args.categories
    elif args.category:
        categories_to_test = [args.category]
    else:
        categories_to_test = []

    if not categories_to_test and not args.validate_only:
        print("\n⚠️ No categories specified for testing. Use --help for usage info.")
        return

    # Create output directory
    output_dir = Path("data_output/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Execute testing
    start_time = time.time()

    if len(categories_to_test) == 1:
        # Single category test
        result = scrape_single_category(
            categories_to_test[0],
            args.max_products,
            args.headless,
            args.debug
        )

        print("\n" + "=" * 60)
        if result['success']:
            print(f"✅ {result['category'].upper()} TEST PASSED!")
            print(f"📁 Output: {result['output_file']}")
            print(f"🔢 Products: {result['product_count']}")
            print(f"⏱️  Time: {result['time_elapsed']}")
        else:
            print(f"❌ {result['category'].upper()} TEST FAILED!")
            print(f"💥 Error: {result['error']}")

    elif categories_to_test:
        # Multi-category test
        results = []
        for i, category in enumerate(categories_to_test, 1):
            print(f"\n📍 TESTING PROGRESS: {i}/{len(categories_to_test)}")

            result = scrape_single_category(
                category,
                args.max_products,
                args.headless,
                args.debug
            )
            results.append(result)

            if i < len(categories_to_test):
                print(f"\n⏳ Waiting {args.delay} seconds before next test...")
                time.sleep(args.delay)

        # Print detailed summary
        print_detailed_summary(results)

    # Calculate and display total time
    total_time = time.time() - start_time
    print(f"\n⏱️  TOTAL TESTING TIME: {total_time:.2f} seconds")


if __name__ == "__main__":
    import logging  # Required for config validation

    main()