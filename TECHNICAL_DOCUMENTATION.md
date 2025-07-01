# Technical Documentation

## Overview

The `ecommerce_scraper` project is a Python-based platform for scraping product data from e-commerce websites, processing and analyzing the data, and generating reports and visualizations. The system is modular, extensible, and designed for both research and production use.

---

## Project Structure

- **main.py**: Entry point for the full scraping, processing, and analysis pipeline. Supports CLI arguments for category, product limits, scrapers, export formats, diagnostics, and more.
- **analyze_data.py**: Command-line tool for data analysis and processing. Supports analysis, processing, and pipeline modes with flexible input/output and export options.
- **run_spider.py**: Utility for running spiders directly.
- **requirements.txt**: Python dependencies.
- **config/**: YAML configuration files for scrapers and global settings.
- **data_output/**: Stores raw, processed, and report data outputs.
- **src/**: Main source code, organized by feature:
  - **scrapers/**: All scraping logic, including site-specific and base scrapers.
  - **data/**: Data models, database integration, and processing utilities.
  - **analysis/**: Statistical analysis, trend detection, and report generation.
  - **cli/**: Command-line interface logic.
  - **utils/**: Helper functions, configuration loaders, and logging.
- **docs/**: Documentation (user guide, API reference, architecture).
- **tests/**: Automated test suite.

---

## Main Modules

### Scrapers
- **src/scrapers/** contains modular scrapers for different e-commerce sites.
- **base_scraper.py**: Abstract base class for all scrapers.
- **selenium_scraper.py** and **static_scraper.py**: For dynamic and static site scraping.
- **zoomer_scraper/**, **alta_scraper/**, **ee_scraper/**: Site-specific implementations.

### Data Processing
- **src/data/processors.py**: Data cleaning, validation, and transformation.
- **src/data/models.py**: Data models and schema definitions.
- **src/data/database.py**: Database integration (if used).

### Analysis
- **src/analysis/statistics.py**: Descriptive and inferential statistics.
- **src/analysis/trends.py**: Trend and time-series analysis.
- **src/analysis/reports.py**: Automated report and visualization generation.

### CLI
- **src/cli/commands.py**: Command definitions for the CLI.
- **src/cli/interface.py**: User interface logic for command-line usage.

### Utilities
- **src/utils/**: Logging, configuration management, and helper functions.

---

## Data Flow

1. **Scraping**: Scrapers collect product data from target websites. The main pipeline (main.py) can run multiple scrapers (Zoomer, Alta, EE) in sequence or individually, with configurable product limits and categories.
2. **Processing**: Data is cleaned, validated, and transformed into a standard format. The pipeline supports combining multiple raw files, validation, cleaning, and export to multiple formats (JSON, CSV, Excel).
3. **Analysis**: Statistical and trend analyses are performed on the processed data. Automated analysis can be triggered from the pipeline or run separately via analyze_data.py.
4. **Reporting**: Results are output as JSON, CSV, Excel, and visual reports (PNG, HTML). Executive summaries and diagnostics reports are also generated.

---

## CLI & Pipeline Usage

- **main.py**: Supports CLI arguments for category, max_products, model_version, scraper selection, process-only, skip-processing, skip-analysis, export-formats, and diagnostics. See the user guide for full argument list and examples.
- **analyze_data.py**: Supports analyze, process, and pipeline commands. Flexible input/output, export format selection, and verbose/debug logging.

---

## Configuration

- **config/scrapers.yaml**: Site-specific scraping settings (selectors, URLs, limits).
- **config/settings.yaml**: Global project settings (output paths, logging, etc.).
- **src/scrapers/zoomer_scraper/zoomer_scraper/settings.py**: Scrapy-specific settings (concurrency, delays, throttling).

---

## Error Handling & Logging

- Centralized logging is provided via `src/utils/logger.py` and enhanced in main.py for pipeline runs. Logs are saved to the logs/ directory with timestamps.
- Error tracking and diagnostics are built into the pipeline. Detailed diagnostics reports (JSON) are generated on demand or when errors occur.
- Warnings and errors are tracked and summarized at the end of each pipeline run.

---

## Extending the Project

- **Add a New Scraper**: Create a new directory in `src/scrapers/`, implement a scraper class, and update configuration files.
- **Add Analysis Features**: Implement new modules in `src/analysis/` and expose them via the CLI.
- **Custom Data Processing**: Extend or modify `src/data/processors.py` for new validation or transformation logic.

---

## Development & Testing

- **Testing**: All core modules are covered by tests in the `tests/` directory. Use `pytest` to run the test suite.
- **Logging**: Centralized logging is provided via `src/utils/logger.py`.
- **Documentation**: User guide, API reference, and architecture docs are in the `docs/` directory.
- **Contribution**: Follow standard Git workflow (feature branches, pull requests, code review).

---

## Dependencies

- scrapy: Web scraping framework
- selenium: For dynamic content scraping
- pandas, numpy, scipy: Data processing and analysis
- matplotlib, seaborn: Visualization
- pyyaml: Configuration file parsing

---

## Output

- **Raw Data**: JSON files in `data_output/raw/`
- **Processed Data**: Cleaned data in `data_output/processed/`
- **Reports**: Visual and textual reports in `data_output/reports/`
- **Diagnostics**: JSON diagnostics reports in `data_output/diagnostics/`

---

## License & Compliance

- Licensed under the MIT License.
- Designed to meet university and industry best practices.

---

For detailed usage instructions, see the user guide in `docs/user_guide.md` and the API reference in `docs/api_reference.md`. 