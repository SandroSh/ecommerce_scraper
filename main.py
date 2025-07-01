import argparse
import os
import sys
import logging
import glob
import traceback
import subprocess
from pathlib import Path
from scrapy.crawler import CrawlerProcess
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add src directory to Python path for imports
sys.path.insert(0, 'src')
from src.data.processors import DataProcessor, DataAggregator

sys.path.insert(0, 'src')
from src.data.processors import DataProcessor, DataAggregator
from src.scrapers.ee_scraper.ee_scraper import EEScraper


class ErrorTracker:
    """Track and report errors during execution"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.start_time = datetime.now()

    def log_error(self, component: str, error: Exception, context: str = ""):
        """Log an error with context"""
        error_info = {
            'timestamp': datetime.now(),
            'component': component,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        self.errors.append(error_info)

    def log_warning(self, component: str, message: str, context: str = ""):
        """Log a warning with context"""
        warning_info = {
            'timestamp': datetime.now(),
            'component': component,
            'message': message,
            'context': context
        }
        self.warnings.append(warning_info)

    def generate_diagnostics_report(self, output_dir: str = "data_output/diagnostics"):
        """Generate comprehensive diagnostics report"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        execution_time = datetime.now() - self.start_time

        report = {
            'execution_summary': {
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'total_execution_time': str(execution_time),
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings)
            },
            'errors': self.errors,
            'warnings': self.warnings,
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform,
                'working_directory': os.getcwd()
            }
        }

        # Save detailed report as JSON
        report_file = f"{output_dir}/diagnostics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(report, f, indent=2, default=str)

        return report_file


class InteractiveExportMenu:
    """Interactive menu for data export options"""

    EXPORT_OPTIONS = {
        '1': (['json'], 'JSON only'),
        '2': (['csv'], 'CSV only'),
        '3': (['excel'], 'Excel only'),
        '4': (['json', 'csv'], 'JSON and CSV'),
        '5': (['json', 'excel'], 'JSON and Excel'),
        '6': (['csv', 'excel'], 'CSV and Excel'),
        '7': (['json', 'csv', 'excel'], 'All formats (JSON, CSV, Excel)')
    }

    @classmethod
    def display_menu(cls):
        """Display export options menu"""
        print("\n" + "=" * 50)
        print("DATA EXPORT OPTIONS")
        print("=" * 50)
        for key, (formats, description) in cls.EXPORT_OPTIONS.items():
            print(f"{key}) {description}")
        print("=" * 50)

    @classmethod
    def get_user_choice(cls) -> List[str]:
        """Get user's export format choice"""
        while True:
            cls.display_menu()
            choice = input("\nSelect export format (1-7): ").strip()

            if choice in cls.EXPORT_OPTIONS:
                formats, description = cls.EXPORT_OPTIONS[choice]
                print(f"\nSelected: {description}")
                return formats
            else:
                print("\nInvalid choice. Please select a number between 1-7.")


def configure_logging():
    """Configure logging with enhanced format"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # FileHandler always supports encoding
    file_handler = logging.FileHandler(f'logs/scraper_{timestamp}.log', encoding='utf-8')

    # StreamHandler with utf-8 encoding (Python 3.9+)
    try:
        stream_handler = logging.StreamHandler(open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1))
    except Exception:
        # Fallback for older Python or if above fails
        stream_handler = logging.StreamHandler(sys.stdout)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[file_handler, stream_handler]
    )


def run_ee_scraper(args, logger, error_tracker):
    """Run EE scraper with BeautifulSoup"""
    try:
        logger.info("🔄 Starting EE scraper...")

        scraper = EEScraper(
            max_products=args.max_products,
            sleep=1.0  # 1 second delay between requests
        )

        products = scraper.run()

        if products and len(products) > 0:
            logger.info(f" EE scraping completed. Found {len(products)} products")
            return True
        else:
            error_tracker.log_warning("EEScraper", "Scraping completed but no products were found",
                                      f"Category: {args.category}")
            logger.warning(" EE scraping completed but no products were found")
            return False

    except ImportError as e:
        error_tracker.log_error("EEScraper", e, "Import error - check if EE scraper dependencies are installed")
        logger.error(f" Failed to import EE scraper: {e}")
        return False
    except Exception as e:
        error_tracker.log_error("EEScraper", e, f"Category: {args.category}, Max products: {args.max_products}")
        logger.error(f" EE scraping failed: {e}")
        return False


def run_zoomer_scraper(args, logger, error_tracker):
    """Run Zoomer scraper with Scrapy"""
    try:
        logger.info("Starting Zoomer scraper...")

        from src.scrapers.zoomer_scraper.zoomer_scraper import settings as spider_settings
        from src.scrapers.zoomer_scraper.zoomer_scraper.spiders.zoomer_spider import ZoomerSpider

        settings = {
            'DOWNLOAD_DELAY': spider_settings.DOWNLOAD_DELAY,
            'CONCURRENT_REQUESTS': spider_settings.CONCURRENT_REQUESTS,
            'CONCURRENT_REQUESTS_PER_DOMAIN': spider_settings.CONCURRENT_REQUESTS_PER_DOMAIN,
            'AUTOTHROTTLE_ENABLED': spider_settings.AUTOTHROTTLE_ENABLED,
            'AUTOTHROTTLE_TARGET_CONCURRENCY': spider_settings.AUTOTHROTTLE_TARGET_CONCURRENCY,
            'AUTOTHROTTLE_START_DELAY': spider_settings.AUTOTHROTTLE_START_DELAY,
            'AUTOTHROTTLE_MAX_DELAY': spider_settings.AUTOTHROTTLE_MAX_DELAY,
            'USER_AGENT': spider_settings.USER_AGENT,
            'LOG_LEVEL': spider_settings.LOG_LEVEL,
            'ROBOTSTXT_OBEY': spider_settings.ROBOTSTXT_OBEY,
            'RANDOMIZE_DOWNLOAD_DELAY': spider_settings.RANDOMIZE_DOWNLOAD_DELAY,
            'DEFAULT_REQUEST_HEADERS': spider_settings.DEFAULT_REQUEST_HEADERS,
            'RETRY_ENABLED': spider_settings.RETRY_ENABLED,
            'RETRY_TIMES': spider_settings.RETRY_TIMES,
            'RETRY_HTTP_CODES': spider_settings.RETRY_HTTP_CODES,
            'LOG_FILE': f'logs/scrapy_zoomer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            'FEEDS': {
                f'data_output/raw/zoomer_{args.category}_{args.max_products}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json': {
                    'format': 'json',
                    'encoding': 'utf8',
                }
            }
        }

        process = CrawlerProcess(settings)
        process.crawl(ZoomerSpider, category=args.category, max_products=args.max_products)
        process.start()

        logger.info("Zoomer scraping completed")
        return True

    except Exception as e:
        error_tracker.log_error("ZoomerScraper", e, f"Category: {args.category}, Max products: {args.max_products}")
        logger.error(f"Zoomer scraping failed: {e}")
        return False


def run_alta_scraper(args, logger, error_tracker):
    """Run Alta scraper with Selenium"""
    try:
        logger.info(" Starting Alta scraper...")

        sys.path.insert(0, 'src/scrapers/alta_scraper')
        from src.scrapers.alta_scraper.alta_selenium_scraper import AltaScraper

        scraper = AltaScraper(
            headless=True,
            max_products=args.max_products,
            debug=False
        )
        filepath = scraper.run(args.category)

        if filepath and os.path.exists(filepath):
            logger.info(f" Alta scraping completed. Data saved to: {filepath}")
            return True
        else:
            error_tracker.log_warning("AltaScraper", "Scraping completed but no data was saved or file not found",
                                      f"Category: {args.category}")
            logger.warning(" Alta scraping completed but no data was saved or file not found")
            return False

    except ImportError as e:
        error_tracker.log_error("AltaScraper", e, "Import error - check if Alta scraper dependencies are installed")
        logger.error(f" Failed to import Alta scraper: {e}")
        return False
    except Exception as e:
        error_tracker.log_error("AltaScraper", e, f"Category: {args.category}, Max products: {args.max_products}")
        logger.error(f" Alta scraping failed: {e}")
        return False


def get_next_incremental_folder(base_dir, prefix):
    """Return the next available folder path as base_dir/prefixN (N=1,2,...)"""
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)
    existing = [d for d in base.iterdir() if d.is_dir() and d.name.startswith(prefix)]
    nums = [int(d.name[len(prefix):]) for d in existing if d.name[len(prefix):].isdigit()]
    next_n = max(nums, default=0) + 1
    next_folder = base / f"{prefix}{next_n}"
    next_folder.mkdir(parents=True, exist_ok=True)
    return str(next_folder)


def process_raw_data_combined(args, logger, error_tracker, export_formats: List[str]):
    """Process and combine cleaned valid data from all raw JSON files into one dataset."""
    try:
        logger.info(" Starting combined data processing...")

        processor = DataProcessor()
        # Create new processedN folder
        processed_dir = get_next_incremental_folder("data_output/processed", "processed")

        raw_data_dir = "data_output/raw"
        raw_files = glob.glob(f"{raw_data_dir}/*.json")

        if not raw_files:
            error_tracker.log_warning("DataProcessor", "No raw data files found", f"Directory: {raw_data_dir}")
            logger.warning("No raw data files found in 'data_output/raw'")
            return False, []

        logger.info(f"Found {len(raw_files)} raw data files")

        cleaned_dfs = []
        total_valid = 0
        total_loaded = 0
        processing_errors = 0

        for file_path in raw_files:
            try:
                logger.info(f" Loading file: {file_path}")
                df = processor.load_raw_data(file_path)
                total_loaded += len(df)

                if df.empty:
                    error_tracker.log_warning("DataProcessor", f"Empty file skipped", f"File: {file_path}")
                    logger.warning(f"Skipping empty file: {file_path}")
                    continue

                valid_df, report = processor.validate_data(df)
                cleaned_df = processor.clean_data(valid_df)

                cleaned_dfs.append(cleaned_df)
                total_valid += len(cleaned_df)

                logger.info(f" {file_path}: {len(cleaned_df)} valid records (from {len(df)})")

            except Exception as e:
                processing_errors += 1
                error_tracker.log_error("DataProcessor", e, f"Processing file: {file_path}")
                logger.error(f" Error processing file {file_path}: {e}")

        # Combine all cleaned records
        if not cleaned_dfs:
            error_tracker.log_error("DataProcessor", Exception("No valid data found"),
                                    f"Processed {len(raw_files)} files, {processing_errors} errors")
            logger.error(" No valid data found in any file")
            return False, []

        combined_df = pd.concat(cleaned_dfs, ignore_index=True)
        logger.info(f" Total valid combined records: {len(combined_df)} (from {total_loaded} scraped)")

        # Export to selected formats in processedN folder
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"{processed_dir}/all_sources_combined_{timestamp}"

        logger.info(f" Exporting data in formats: {', '.join(export_formats)}")
        exported = processor.export_data(combined_df, output_path, formats=export_formats)

        logger.info(" Combined export completed")
        for fmt, path in exported.items():
            logger.info(f"   {fmt.upper()}: {path}")

        return processed_dir, raw_files  # Return processed dir and raw files for later use

    except Exception as e:
        error_tracker.log_error("DataProcessor", e, "Combined data processing")
        logger.error(f" Data processing failed: {e}")
        return False, []


def run_automated_analysis(logger, error_tracker, processed_dir=None):
    """Automatically run data analysis after processing"""
    try:
        logger.info("Starting automated data analysis...")

        # Check if analyze_data.py exists
        analysis_script = "analyze_data.py"
        if not os.path.exists(analysis_script):
            error_tracker.log_warning("AutoAnalysis", f"Analysis script not found: {analysis_script}",
                                      "Skipping automated analysis")
            logger.warning(f" {analysis_script} not found. Skipping automated analysis.")
            return False

        # Create new reportN folder
        report_dir = get_next_incremental_folder("data_output/reports", "report")

        # Run the analysis script with processed_dir and report_dir
        result = subprocess.run([sys.executable, analysis_script, processed_dir, report_dir],
                                capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            logger.info(" Automated data analysis completed successfully")
            if result.stdout:
                logger.info("Analysis output:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        logger.info(f"  {line}")
            return report_dir
        else:
            error_tracker.log_error("AutoAnalysis",
                                    Exception(f"Analysis script failed with return code {result.returncode}"),
                                    f"stderr: {result.stderr}")
            logger.error(f" Analysis script failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        error_tracker.log_error("AutoAnalysis", Exception("Analysis script timeout"),
                                "Script took longer than 5 minutes")
        logger.error(" Analysis script timed out (5 minutes)")
        return False
    except Exception as e:
        error_tracker.log_error("AutoAnalysis", e, "Running automated analysis")
        logger.error(f" Failed to run automated analysis: {e}")
        return False


def print_execution_summary(error_tracker, logger, scraping_success, processing_success, analysis_success):
    """Print comprehensive execution summary"""
    print("\n" + "=" * 80)
    print(" EXECUTION SUMMARY")
    print("=" * 80)

    execution_time = datetime.now() - error_tracker.start_time

    print(f"  Total execution time: {execution_time}")
    print(f" Scraping: {'SUCCESS' if scraping_success else 'FAILED'}")
    print(f" Processing: {'SUCCESS' if processing_success else 'FAILED'}")
    print(f" Analysis: {'SUCCESS' if analysis_success else 'FAILED/SKIPPED'}")

    if error_tracker.errors:
        print(f"\n Errors encountered: {len(error_tracker.errors)}")
        for i, error in enumerate(error_tracker.errors[-3:], 1):  # Show last 3 errors
            print(f"   {i}. {error['component']}: {error['error_type']} - {error['error_message']}")
        if len(error_tracker.errors) > 3:
            print(f"   ... and {len(error_tracker.errors) - 3} more errors")

    if error_tracker.warnings:
        print(f"\n  Warnings: {len(error_tracker.warnings)}")
        for i, warning in enumerate(error_tracker.warnings[-3:], 1):  # Show last 3 warnings
            print(f"   {i}. {warning['component']}: {warning['message']}")
        if len(error_tracker.warnings) > 3:
            print(f"   ... and {len(error_tracker.warnings) - 3} more warnings")

    print("=" * 80)


def main():
    configure_logging()
    logger = logging.getLogger(__name__)
    error_tracker = ErrorTracker()

    parser = argparse.ArgumentParser(description='Run E-commerce product scraper and data processor (Zoomer, Alta, EE)')
    parser.add_argument('--category', type=str, default='phones',
                        choices=['phones', 'fridges', 'laptops', 'tvs'],
                        help='Product category to scrape')
    parser.add_argument('--max_products', type=int, default=10,
                        help='Maximum number of products to scrape')
    parser.add_argument('--model_version', type=str, default='v1',
                        choices=['v1', 'v2', 'v3'],
                        help='Data processing model version')
    parser.add_argument('--scraper', type=str, default='all',
                        choices=['zoomer', 'alta', 'ee', 'both', 'all'],
                        help='Which scraper to run (both = zoomer+alta, all = zoomer+alta+ee)')
    parser.add_argument('--process-only', action='store_true',
                        help='Skip scraping and only process existing raw data')
    parser.add_argument('--skip-processing', action='store_true',
                        help='Skip data processing after scraping')
    parser.add_argument('--skip-analysis', action='store_true',
                        help='Skip automated analysis after processing')
    parser.add_argument('--export-formats', type=str, nargs='+',
                        choices=['json', 'csv', 'excel'],
                        help='Export formats (bypasses interactive menu)')
    parser.add_argument('--generate-diagnostics', action='store_true',
                        help='Generate detailed diagnostics report')

    args = parser.parse_args()

    try:
        logger.info("Starting E-commerce Data Pipeline")
        logger.info("=" * 60)
        logger.info(f"  Category: {args.category}")
        logger.info(f"  Max products: {args.max_products}")
        scraper_description = {
            'zoomer': 'Zoomer only',
            'alta': 'Alta only',
            'ee': 'EE only',
            'both': 'Zoomer + Alta',
            'all': 'Zoomer + Alta + EE'
        }
        logger.info(f" Scraper: {scraper_description.get(args.scraper, args.scraper)}")
        logger.info(f"  Process only: {args.process_only}")
        logger.info(f"  Skip processing: {args.skip_processing}")
        logger.info(f"  Skip analysis: {args.skip_analysis}")
        logger.info("=" * 60)

        scraping_success = True
        processing_success = True
        analysis_success = True

        processed_dir = None
        raw_files = []
        if not args.process_only:
            logger.info(" PHASE 1: DATA SCRAPING")
            scraping_results = []

            if args.scraper in ['zoomer', 'both', 'all']:
                result = run_zoomer_scraper(args, logger, error_tracker)
                scraping_results.append(result)

            if args.scraper in ['alta', 'both', 'all']:
                result = run_alta_scraper(args, logger, error_tracker)
                scraping_results.append(result)

            # ADD this new section:
            if args.scraper in ['ee', 'all']:
                result = run_ee_scraper(args, logger, error_tracker)
                scraping_results.append(result)

            scraping_success = any(scraping_results) if scraping_results else False

            if not scraping_success:
                error_tracker.log_error("Pipeline", Exception("All scrapers failed"), "Scraping phase")
                logger.error(" All scrapers failed!")

        # Processing phase
        if not args.skip_processing:
            logger.info("\n PHASE 2: DATA PROCESSING")
            if args.export_formats:
                export_formats = args.export_formats
                logger.info(f"Using command-line export formats: {export_formats}")
            else:
                export_formats = InteractiveExportMenu.get_user_choice()
            processed_dir, raw_files = process_raw_data_combined(args, logger, error_tracker, export_formats)
        else:
            logger.info(" Skipping data processing phase")

        # Analysis phase
        report_dir = None
        if not args.skip_analysis and processed_dir:
            logger.info("\n PHASE 3: AUTOMATED ANALYSIS")
            report_dir = run_automated_analysis(logger, error_tracker, processed_dir)
        else:
            if args.skip_analysis:
                logger.info("  Skipping automated analysis phase")
            else:
                logger.info("  Skipping analysis due to processing failure")
                analysis_success = False

        # Generate diagnostics report
        if args.generate_diagnostics or error_tracker.errors:
            logger.info("\n GENERATING DIAGNOSTICS REPORT")
            diagnostics_file = error_tracker.generate_diagnostics_report()
            logger.info(f" Diagnostics report saved: {diagnostics_file}")

        # Delete raw files after processing and analysis
        if raw_files:
            for f in raw_files:
                try:
                    os.remove(f)
                    logger.info(f"Deleted raw file: {f}")
                except Exception as e:
                    logger.warning(f"Failed to delete raw file {f}: {e}")

        # Print final summary
        print_execution_summary(error_tracker, logger, scraping_success, processing_success, analysis_success)

        if scraping_success and processing_success:
            logger.info("\n Pipeline completed successfully!")
        else:
            logger.warning("\n  Pipeline completed with some failures. Check logs for details.")

    except KeyboardInterrupt:
        error_tracker.log_error("Pipeline", Exception("User interrupted execution"), "KeyboardInterrupt")
        logger.error("\n Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        error_tracker.log_error("Pipeline", e, "Main execution")
        logger.error(f"\n Unexpected error in main execution: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()