# Technical Documentation

## Project Overview
This document provides technical details about the `ecommerce_scraper` project, including its architecture, main components, and data flow.

## Directory Structure
- **src/**: Main source code, organized by feature (scrapers, data, analysis, cli, utils).
- **config/**: Configuration files for scrapers and settings.
- **data_output/**: Output data from scrapers, processed data, reports, and diagnostics.
- **docs/**: Documentation files (API reference, user guide, architecture).
- **tests/**: Test suite for the project.

## Main Components
- **Scrapers**: Located in `src/scrapers/`, includes site-specific and base scrapers. Supports multiple sites (Zoomer, Alta, EE) and can be run individually or together via the main pipeline.
- **Data Processing**: Handled in `src/data/` (models, database, processors). Cleans, validates, and standardizes data, supports multi-format export.
- **Analysis**: Reporting and statistics in `src/analysis/`. Generates statistical summaries, trend analysis, and visualizations.
- **CLI**: Command-line interface in `src/cli/`. Main entry points are `main.py` (pipeline) and `analyze_data.py` (analysis/processing).
- **Utilities**: Helper functions and logging in `src/utils/`. Centralized logging and diagnostics support.

## Data Flow
1. **Scraping**: Scrapers collect data from e-commerce sites. The main pipeline (main.py) can run multiple scrapers in sequence or individually, with configurable product limits and categories.
2. **Processing**: Data is cleaned, validated, and stored using processors and models. Supports combining multiple raw files and exporting to JSON, CSV, and Excel.
3. **Analysis**: Data is analyzed for trends and statistics. Automated analysis and reporting can be triggered from the pipeline or run separately.
4. **Output**: Results are saved in `data_output/` as processed data, reports, and diagnostics. Visualizations and executive summaries are generated.

## Configuration
- **scrapers.yaml**: Defines scraper-specific settings.
- **settings.yaml**: General project settings.
- **src/scrapers/zoomer_scraper/zoomer_scraper/settings.py**: Scrapy-specific settings (concurrency, delays, throttling).

## Error Handling & Logging
- Centralized logging is provided via `src/utils/logger.py` and enhanced in main.py for pipeline runs. Logs are saved to the logs/ directory with timestamps.
- Error tracking and diagnostics are built into the pipeline. Detailed diagnostics reports (JSON) are generated on demand or when errors occur.
- Warnings and errors are tracked and summarized at the end of each pipeline run.

## Extending the Project
- Add new scrapers in `src/scrapers/`.
- Implement new analysis modules in `src/analysis/`.
- Update configuration files as needed.

---

*For more details, see the API reference and user guide in the docs directory.*
