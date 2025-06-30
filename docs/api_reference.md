# API Reference

This document provides an overview of the main classes and functions available in the `ecommerce_scraper` project. It is intended for developers and advanced users who want to extend or integrate with the platform.

---

## Data Processing

### `DataProcessor`
Located in: `src/data/processors.py`

Handles data loading, validation, cleaning, and feature extraction for e-commerce product data.

**Key Methods:**
- `__init__(config: Optional[Dict] = None)`: Initialize with optional configuration.
- `load_raw_data(file_path: str) -> pd.DataFrame`: Load raw JSON data into a DataFrame.
- `validate_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]`: Validate data against rules and return cleaned data with a validation report.
- `clean_data(df: pd.DataFrame) -> pd.DataFrame`: Clean and standardize data fields, extract features, and compute quality scores.
- `export_data(df: pd.DataFrame, output_path: str, formats: List[str] = None) -> Dict[str, str]`: Export cleaned data to various formats (JSON, CSV, Excel).
- `process_file(input_path: str, output_dir: str = None) -> Dict[str, Any]`: Complete pipeline for loading, validating, cleaning, and exporting data.

---

## Statistical Analysis

### `StatisticalAnalyzer`
Located in: `src/analysis/statistics.py`

Performs comprehensive statistical analysis on product data.

**Key Methods:**
- `__init__(data: pd.DataFrame)`: Initialize with a DataFrame.
- `descriptive_statistics() -> Dict[str, Any]`: Generate descriptive statistics (counts, means, medians, distributions).
- `price_distribution_analysis() -> Dict[str, Any]`: Analyze price distributions, outliers, and segments.
- `brand_analysis() -> Dict[str, Any]`: Analyze brand market share and price positioning.
- `category_analysis() -> Dict[str, Any]`: Analyze product categories and their characteristics.
- `correlation_analysis() -> Dict[str, Any]`: Compute correlations between numeric fields.
- `time_series_analysis() -> Dict[str, Any]`: Analyze time-based trends and patterns.
- `generate_summary_report() -> Dict[str, Any]`: Generate a summary report with key findings.

---

## Report Generation

### `ReportGenerator`
Located in: `src/analysis/reports.py`

Generates executive summaries, detailed reports, and visualizations from analyzed data.

**Key Methods:**
- `__init__(data: pd.DataFrame, output_dir: str = "data_output/reports")`: Initialize with data and output directory.
- `generate_executive_summary() -> Dict[str, Any]`: Create a summary with key insights and statistics.
- `create_visualizations() -> Dict[str, str]`: Generate and save charts (price, category, brand, time series).
- `generate_detailed_report() -> Dict[str, Any]`: Produce a detailed, multi-section report.
- `export_report(report_data: Dict[str, Any], format: str = 'json') -> str`: Export report in JSON or HTML format.
- `generate_complete_report() -> Dict[str, str]`: Run the full reporting pipeline and return file paths.

---

## Scraping

### `EEScraper`
Located in: `src/scrapers/ee_scraper/ee_scraper.py`

A robust scraper for extracting product data from the EE.ge website.

**Key Methods:**
- `__init__(max_products=100, sleep=1.0)`: Initialize with product limit and request delay.
- `clean_price_to_number(price_text)`: Convert price text to a numeric value.
- `get_all_listing_pages()`: Retrieve all product listing page URLs.
- `get_product_links(page_url)`: Extract product links from a listing page.
- `parse_product_details(product_url)`: Parse detailed product information from a product page.
- `run()`: Execute the full scraping workflow.

---

## Utilities

### `get_logger`
Located in: `src/utils/logger.py`

- `get_logger(name: str = "scraper", log_file: str = "scraper.log") -> logging.Logger`: Returns a configured logger instance for use throughout the project.

---

## Data Helpers

Located in: `src/utils/data_helpers.py`

- `save_products_to_json(products: List, filename: str = "products.json")`: Save product data to a JSON file.
- `save_products_to_csv(products: List[Product], filename: str = "products.csv")`: Save product data to a CSV file.
- `extract_brand_from_name(name: str) -> str`: Extract brand name from a product name string.
- `clean_price(price_text: str) -> str`: Clean and standardize price text.

---

For more details on additional modules (such as AltaScraper, ZoomerSpider, pipelines, and middlewares), see the respective source files in the `src/scrapers/` directory.
