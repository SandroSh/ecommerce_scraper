"""
E-commerce Data Analysis Tool

This module provides a comprehensive data analysis pipeline for ecommerce scraped data.
It includes data processing, analysis, and reporting capabilities with support for
multiple input formats and export options.

The module supports three main operations:
- process: Process individual data files with cleaning and validation
- analyze: Generate comprehensive analysis reports from processed data
- pipeline: Complete end-to-end processing and analysis workflow

Features:
- Multi-format data processing (JSON, CSV, Excel)
- Data quality assessment and validation
- Statistical analysis and reporting
- Automated report generation
- Configurable output formats
- Comprehensive logging and error handling
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data.processors import DataProcessor, DataAggregator
from src.analysis.reports import ReportGenerator, create_analysis_pipeline


def setup_logging():
    """
    Configure logging for the data analysis tool.
    
    Sets up logging with both file and console output, using a consistent
    format that includes timestamps, logger names, and log levels. The
    log file is named 'analysis.log'.
    
    The logging configuration applies to the entire analysis process and
    ensures consistent logging across all components.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('analysis.log'),
            logging.StreamHandler()
        ]
    )


def process_single_file(input_file: str, output_dir: Optional[str] = None):
    """
    Process a single data file with cleaning, validation, and export.
    
    This function processes an individual data file through the complete
    data processing pipeline, including data cleaning, validation, quality
    assessment, and export to multiple formats.
    
    Args:
        input_file (str): Path to the input data file to process
        output_dir (Optional[str]): Output directory for processed files.
                                  Defaults to "data_output/processed"
    
    Returns:
        bool: True if processing was successful, False otherwise
    """
    if output_dir is None:
        output_dir = "data_output/processed"
    
    processor = DataProcessor()
    
    print(f"Processing file: {input_file}")
    result = processor.process_file(input_file, output_dir)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return False
    
    print(f"Processing complete!")
    print(f"- Original records: {result['original_records']}")
    print(f"- Processed records: {result['processed_records']}")
    print(f"- Data quality average: {result['data_quality_avg']:.1f}/100")
    print(f"- Validation rate: {result['validation_report']['validation_rate']:.1%}")
    
    print("\nExported files:")
    for fmt, filepath in result['exported_files'].items():
        print(f"- {fmt.upper()}: {filepath}")
    
    return True


def analyze_data(input_files: list, output_dir: Optional[str] = None):
    """
    Analyze processed data and generate comprehensive reports.
    
    This function performs statistical analysis on processed data files
    and generates various types of reports including summary statistics,
    trend analysis, and data quality reports.
    
    Args:
        input_files (list): List of processed data file paths to analyze
        output_dir (Optional[str]): Output directory for analysis reports.
                                  Defaults to "data_output/reports"
    
    Returns:
        bool: True if analysis was successful, False otherwise
    """
    if output_dir is None:
        output_dir = "data_output/reports"
    
    print(f"Analyzing {len(input_files)} data files...")
    
    try:
        results = create_analysis_pipeline(input_files, output_dir)
        
        if 'error' in results:
            print(f"Error: {results['error']}")
            return False
        
        print(f"\nAnalysis complete!")
        print(f"- Total records analyzed: {results['total_records_processed']:,}")
        print(f"- Output directory: {results['output_directory']}")
        
        print("\nGenerated files:")
        for file_type, filepath in results['generated_files'].items():
            print(f"- {file_type}: {filepath}")
        
        return True
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        return False


def main():
    """
    Main command-line interface for the ecommerce data analysis tool.
    
    This function provides a comprehensive CLI for data processing and analysis
    operations. It supports three main commands:
    
    - process: Process individual data files with cleaning and validation
    - analyze: Generate analysis reports from processed data
    - pipeline: Complete end-to-end processing and analysis workflow
    
    The function includes comprehensive argument parsing, input validation,
    error handling, and status reporting.
    
    Command-line arguments:
        command: The operation to perform (process/analyze/pipeline)
        --input: Input file(s) to process or analyze
        --output: Output directory for results
        --formats: Export formats for processed data
    """
    parser = argparse.ArgumentParser(description='E-commerce Data Analysis Tool')
    parser.add_argument('command', choices=['process', 'analyze', 'pipeline'], 
                       help='Command to execute')
    parser.add_argument('--input', '-i', required=True, nargs='+',
                       help='Input file(s) to process/analyze')
    parser.add_argument('--output', '-o', 
                       help='Output directory (default: data_output/processed or data_output/reports)')
    parser.add_argument('--formats', nargs='+', default=['json', 'csv', 'excel'],
                       choices=['json', 'csv', 'excel'],
                       help='Export formats for processed data')
    
    args = parser.parse_args()
    
    setup_logging()
    
    # Validate input files
    for input_file in args.input:
        if not os.path.exists(input_file):
            print(f"Error: Input file not found: {input_file}")
            sys.exit(1)
    
    success = False
    
    if args.command == 'process':
        # Process individual files
        for input_file in args.input:
            success = process_single_file(input_file, args.output)
            if not success:
                break
    
    elif args.command == 'analyze':
        # Analyze data and generate reports
        success = analyze_data(args.input, args.output)
    
    elif args.command == 'pipeline':
        # Complete pipeline: process then analyze
        print("Running complete data processing and analysis pipeline...")
        
        # Step 1: Process all files
        processed_files = []
        processor = DataProcessor()
        
        for input_file in args.input:
            print(f"\nProcessing: {input_file}")
            result = processor.process_file(input_file, args.output or "data_output/processed")
            
            if 'error' not in result and result['exported_files'].get('json'):
                processed_files.append(result['exported_files']['json'])
                print(f"✓ Processed: {result['processed_records']} records")
            else:
                print(f"✗ Failed to process {input_file}")
        
        # Step 2: Analyze processed files
        if processed_files:
            print(f"\nAnalyzing {len(processed_files)} processed files...")
            success = analyze_data(processed_files, args.output or "data_output/reports")
        else:
            print("No files were successfully processed for analysis")
            success = False
    
    if success:
        print("\n✓ Operation completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()