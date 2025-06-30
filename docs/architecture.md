# Technical Documentation

## Project Overview
This document provides technical details about the `ecommerce_scraper` project, including its architecture, main components, and data flow.

## Directory Structure
- **src/**: Main source code, organized by feature (scrapers, data, analysis, cli, utils).
- **config/**: Configuration files for scrapers and settings.
- **data_output/**: Output data from scrapers.
- **docs/**: Documentation files (API reference, user guide, architecture).
- **tests/**: Test suite for the project.

## Main Components
- **Scrapers**: Located in `src/scrapers/`, includes site-specific and base scrapers.
- **Data Processing**: Handled in `src/data/` (models, database, processors).
- **Analysis**: Reporting and statistics in `src/analysis/`.
- **CLI**: Command-line interface in `src/cli/`.
- **Utilities**: Helper functions and logging in `src/utils/`.

## Data Flow
1. **Scraping**: Scrapers collect data from e-commerce sites.
2. **Processing**: Data is cleaned and stored using processors and models.
3. **Analysis**: Data is analyzed for trends and statistics.
4. **Output**: Results are saved in `data_output/` and can be accessed via reports.

## Configuration
- **scrapers.yaml**: Defines scraper-specific settings.
- **settings.yaml**: General project settings.

## Extending the Project
- Add new scrapers in `src/scrapers/`.
- Implement new analysis modules in `src/analysis/`.
- Update configuration files as needed.

---

*For more details, see the API reference and user guide in the docs directory.*
