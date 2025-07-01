# User Guide

Welcome to the user guide for the `ecommerce_scraper` platform. This guide will help you get started with installation, configuration, running scrapers, analyzing data, and interpreting results.

---

## 1. Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ecommerce_scraper
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Create output directories:**
   ```bash
   mkdir -p data_output/{raw,processed,reports}
   ```

---

## 2. Configuration

- **Scraper settings:**
  - Edit `config/scrapers.yaml` for site-specific scraping options.
  - Edit `config/settings.yaml` for general project settings.
- **Scrapy settings:**
  - Adjust concurrency, delays, and throttling in `src/scrapers/zoomer_scraper/zoomer_scraper/settings.py`.

---

## 3. Basic Usage

### Scraping Data
Run the main pipeline to collect product data:
```bash
python main.py --category phones --max_products 10
```
- Replace `phones` with `laptops`, `fridges`, or `tvs` for other categories.
- Adjust `--max_products` to control the number of products scraped.
- Use `--scraper` to select which scraper(s) to run: `zoomer`, `alta`, `ee`, `both`, or `all`.
- Use `--process-only` to skip scraping and process existing raw data.
- Use `--skip-processing` or `--skip-analysis` to skip those pipeline phases.
- Use `--export-formats` to specify output formats (json, csv, excel).
- Use `--generate-diagnostics` to create a diagnostics report.

### Analyzing Data
Analyze the scraped data using the analysis CLI:
```bash
python analyze_data.py analyze --input data_output/raw/zoomer_phones_10.json
```

### Complete Pipeline
Run the full pipeline (scrape, process, analyze):
```bash
python main.py --category phones --max_products 100
python analyze_data.py pipeline --input data_output/raw/zoomer_phones_100.json --output data_output/phone_analysis
```

---

## 4. Workflow Example

**Scenario: Analyze 100 phone products**
```bash
# Scrape 100 phone products
python main.py --category phones --max_products 100

# Run analysis pipeline
python analyze_data.py pipeline --input data_output/raw/zoomer_phones_100.json --output data_output/phone_analysis_100

# View results
ls data_output/phone_analysis_100/
```
**Typical output files:**
- `ecommerce_analysis_report_[timestamp].json`  (Detailed JSON report)
- `ecommerce_analysis_report_[timestamp].html`  (HTML dashboard)
- `price_distribution.png`                      (Price analysis charts)
- `category_analysis.png`                       (Category breakdown)
- `brand_analysis.png`                          (Brand market share)
- `time_analysis.png`                           (Time-based patterns)
- `report_summary_[timestamp].txt`              (Executive summary)
- `zoomer_phones_100_processed_[timestamp].csv` (Clean data export)

---

## 5. Advanced Usage

- **Process existing data:**
  ```bash
  python analyze_data.py process --input data_output/raw/zoomer_phones_50.json --output data_output/processed
  ```
- **Analyze multiple files:**
  ```bash
  python analyze_data.py analyze --input data_output/raw/zoomer_phones_50.json data_output/raw/zoomer_laptops_30.json --output data_output/combined_analysis
  ```
- **Custom output directory:**
  ```bash
  python analyze_data.py pipeline --input data_output/raw/zoomer_laptops_100.json --output /custom/path/laptop_reports
  ```
- **Select export formats:**
  ```bash
  python analyze_data.py process --input data.json --formats json csv excel
  ```

---

## 6. Output Interpretation

- **JSON/HTML Reports:** Contain detailed statistics, trends, and key insights.
- **PNG Charts:** Visualize price distributions, category breakdowns, brand shares, and time trends.
- **CSV/Excel:** Cleaned and validated product data for further analysis.
- **Text Summaries:** Executive summaries with main findings.

---

## 7. Troubleshooting

- **Import errors:**
  - Ensure all dependencies are installed: `pip install -r requirements.txt`
- **Empty results:**
  - Check that the data file exists and is valid JSON.
- **Permission errors:**
  - Make sure output directories exist and you have write permissions.
- **Rate limiting:**
  - The scraper handles rate limiting automatically. Adjust `DOWNLOAD_DELAY` in settings if needed.
- **Debug mode:**
  - Enable verbose logging: `python analyze_data.py analyze --input data.json --verbose`
- **Diagnostics:**
  - Use `--generate-diagnostics` with main.py to generate a detailed diagnostics report after pipeline execution.

---

## 8. Data Schema

**Raw data example:**
```json
{
  "source": "zoommer.ge",
  "name": "Apple iPhone 16 Pro Max 256GB",
  "price": 3299,
  "brand": "Apple",
  "category": "phones",
  "description": "Detailed product specifications...",
  "createdat": "2025-06-28T17:08:36.141170"
}
```

**Processed data features:**
- Data quality score (0-100)
- Extracted features (storage, RAM, etc.)
- Standardized fields (cleaned text, normalized prices)
- Derived time features (date, hour, weekday)

---

## 9. Contributing

- Fork the repository and create a feature branch.
- Commit and push your changes.
- Open a pull request for review.

---

