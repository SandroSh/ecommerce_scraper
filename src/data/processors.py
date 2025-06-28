"""
Data processing and cleaning pipeline for e-commerce scraped data.
Implements data validation, cleaning, and transformation operations.
"""

import json
import pandas as pd
import numpy as np
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path

class DataProcessor:
    """Main data processing class for cleaning and validating scraped data."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.validation_rules = self._init_validation_rules()
        
    def _init_validation_rules(self) -> Dict:
        """Initialize data validation rules."""
        return {
            'required_fields': ['source', 'name', 'price', 'brand', 'category', 'createdat'],
            'price_range': {'min': 0, 'max': 50000},  # GEL
            'valid_categories': ['phones', 'laptops', 'fridges', 'tvs'],
            'valid_sources': ['zoommer.ge'],
            'name_min_length': 3,
            'brand_min_length': 1
        }
    
    def load_raw_data(self, file_path: str) -> pd.DataFrame:
        """Load raw JSON data and convert to DataFrame."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                data = [data]
                
            df = pd.DataFrame(data)
            self.logger.info(f"Loaded {len(df)} records from {file_path}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading data from {file_path}: {e}")
            return pd.DataFrame()
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Validate data against predefined rules and return cleaned data + validation report."""
        validation_report = {
            'total_records': len(df),
            'valid_records': 0,
            'issues': {
                'missing_fields': [],
                'invalid_prices': [],
                'invalid_categories': [],
                'invalid_sources': [],
                'invalid_names': [],
                'invalid_brands': [],
                'invalid_dates': []
            }
        }
        
        if df.empty:
            return df, validation_report
        
        # Check required fields
        missing_fields = set(self.validation_rules['required_fields']) - set(df.columns)
        if missing_fields:
            validation_report['issues']['missing_fields'] = list(missing_fields)
            self.logger.warning(f"Missing required fields: {missing_fields}")
        
        # Validate each record
        valid_indices = []
        
        for idx, row in df.iterrows():
            is_valid = True
            
            # Check for null values in required fields
            for field in self.validation_rules['required_fields']:
                if field in df.columns and (pd.isna(row[field]) or row[field] == ''):
                    validation_report['issues']['missing_fields'].append(f"Row {idx}: missing {field}")
                    is_valid = False
            
            # Validate price
            if 'price' in df.columns:
                try:
                    price = float(row['price'])
                    if not (self.validation_rules['price_range']['min'] <= price <= self.validation_rules['price_range']['max']):
                        validation_report['issues']['invalid_prices'].append(f"Row {idx}: price {price} out of range")
                        is_valid = False
                except (ValueError, TypeError):
                    validation_report['issues']['invalid_prices'].append(f"Row {idx}: invalid price format")
                    is_valid = False
            
            # Validate category
            if 'category' in df.columns and row['category'] not in self.validation_rules['valid_categories']:
                validation_report['issues']['invalid_categories'].append(f"Row {idx}: invalid category '{row['category']}'")
                is_valid = False
            
            # Validate source
            if 'source' in df.columns and row['source'] not in self.validation_rules['valid_sources']:
                validation_report['issues']['invalid_sources'].append(f"Row {idx}: invalid source '{row['source']}'")
                is_valid = False
            
            # Validate name
            if 'name' in df.columns:
                name = str(row['name']).strip()
                if len(name) < self.validation_rules['name_min_length']:
                    validation_report['issues']['invalid_names'].append(f"Row {idx}: name too short")
                    is_valid = False
            
            # Validate brand
            if 'brand' in df.columns:
                brand = str(row['brand']).strip()
                if len(brand) < self.validation_rules['brand_min_length']:
                    validation_report['issues']['invalid_brands'].append(f"Row {idx}: brand too short")
                    is_valid = False
            
            # Validate date format
            if 'createdat' in df.columns:
                try:
                    datetime.fromisoformat(row['createdat'].replace('Z', '+00:00'))
                except (ValueError, TypeError, AttributeError):
                    validation_report['issues']['invalid_dates'].append(f"Row {idx}: invalid date format")
                    is_valid = False
            
            if is_valid:
                valid_indices.append(idx)
        
        # Filter to valid records
        clean_df = df.loc[valid_indices].copy()
        validation_report['valid_records'] = len(clean_df)
        validation_report['validation_rate'] = len(clean_df) / len(df) if len(df) > 0 else 0
        
        self.logger.info(f"Validation complete: {len(clean_df)}/{len(df)} records valid ({validation_report['validation_rate']:.2%})")
        
        return clean_df, validation_report
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize data."""
        if df.empty:
            return df
        
        cleaned_df = df.copy()
        
        # Clean text fields
        text_fields = ['name', 'brand', 'description']
        for field in text_fields:
            if field in cleaned_df.columns:
                cleaned_df[field] = cleaned_df[field].astype(str).str.strip()
                # Remove extra whitespace
                cleaned_df[field] = cleaned_df[field].str.replace(r'\s+', ' ', regex=True)
        
        # Standardize prices
        if 'price' in cleaned_df.columns:
            cleaned_df['price'] = pd.to_numeric(cleaned_df['price'], errors='coerce')
        
        # Parse and standardize dates
        if 'createdat' in cleaned_df.columns:
            cleaned_df['createdat'] = pd.to_datetime(cleaned_df['createdat'], errors='coerce')
            # Add derived date fields
            cleaned_df['scrape_date'] = cleaned_df['createdat'].dt.date
            cleaned_df['scrape_hour'] = cleaned_df['createdat'].dt.hour
            cleaned_df['scrape_weekday'] = cleaned_df['createdat'].dt.day_name()
        
        # Extract features from product names
        if 'name' in cleaned_df.columns:
            # Extract storage capacity (GB/TB)
            cleaned_df['storage_gb'] = cleaned_df['name'].str.extract(r'(\d+)GB', expand=False).astype(float)
            cleaned_df['storage_tb'] = cleaned_df['name'].str.extract(r'(\d+)TB', expand=False).astype(float)
            # Convert TB to GB
            cleaned_df.loc[cleaned_df['storage_tb'].notna(), 'storage_gb'] = cleaned_df['storage_tb'] * 1024
            
            # Extract RAM (for laptops)
            cleaned_df['ram_gb'] = cleaned_df['name'].str.extract(r'(\d+)GB.*RAM|RAM.*(\d+)GB', expand=False)[0].astype(float)
        
        # Add data quality score
        cleaned_df['data_quality_score'] = self._calculate_quality_score(cleaned_df)
        
        self.logger.info(f"Data cleaning complete: {len(cleaned_df)} records processed")
        
        return cleaned_df
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate data quality score for each record (0-100)."""
        scores = pd.Series(100, index=df.index)  # Start with perfect score
        
        # Deduct points for missing or poor quality data
        if 'description' in df.columns:
            # Deduct points for short descriptions
            short_desc = df['description'].str.len() < 50
            scores.loc[short_desc] -= 20
        
        if 'name' in df.columns:
            # Deduct points for very short names
            short_name = df['name'].str.len() < 10
            scores.loc[short_name] -= 15
        
        # Deduct points for missing derived features
        if 'storage_gb' in df.columns:
            missing_storage = df['storage_gb'].isna()
            scores.loc[missing_storage] -= 10
        
        return scores.clip(lower=0)
    
    def export_data(self, df: pd.DataFrame, output_path: str, formats: List[str] = None) -> Dict[str, str]:
        """Export cleaned data in multiple formats."""
        if formats is None:
            formats = ['json', 'csv', 'excel']
        
        exported_files = {}
        base_path = Path(output_path)
        base_path.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for fmt in formats:
            try:
                if fmt == 'json':
                    file_path = f"{base_path}_{timestamp}.json"
                    df.to_json(file_path, orient='records', date_format='iso', indent=2)
                    exported_files['json'] = file_path
                    
                elif fmt == 'csv':
                    file_path = f"{base_path}_{timestamp}.csv"
                    df.to_csv(file_path, index=False, encoding='utf-8')
                    exported_files['csv'] = file_path
                    
                elif fmt == 'excel':
                    file_path = f"{base_path}_{timestamp}.xlsx"
                    df.to_excel(file_path, index=False, engine='openpyxl')
                    exported_files['excel'] = file_path
                    
                self.logger.info(f"Exported {len(df)} records to {file_path}")
                
            except Exception as e:
                self.logger.error(f"Error exporting to {fmt}: {e}")
        
        return exported_files
    
    def process_file(self, input_path: str, output_dir: str = None) -> Dict[str, Any]:
        """Complete processing pipeline for a single file."""
        if output_dir is None:
            output_dir = "data_output/processed"
        
        # Load data
        df = self.load_raw_data(input_path)
        if df.empty:
            return {'error': 'No data loaded'}
        
        # Validate data
        clean_df, validation_report = self.validate_data(df)
        
        # Clean data
        final_df = self.clean_data(clean_df)
        
        # Export results
        input_filename = Path(input_path).stem
        output_path = f"{output_dir}/{input_filename}_processed"
        exported_files = self.export_data(final_df, output_path)
        
        # Create processing report
        processing_report = {
            'input_file': input_path,
            'processing_timestamp': datetime.now().isoformat(),
            'original_records': len(df),
            'processed_records': len(final_df),
            'data_quality_avg': final_df['data_quality_score'].mean() if 'data_quality_score' in final_df.columns else None,
            'validation_report': validation_report,
            'exported_files': exported_files
        }
        
        return processing_report


class DataAggregator:
    """Aggregate data from multiple sources and time periods."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def aggregate_files(self, file_paths: List[str]) -> pd.DataFrame:
        """Aggregate multiple processed data files."""
        all_dfs = []
        processor = DataProcessor()
        
        for file_path in file_paths:
            try:
                df = processor.load_raw_data(file_path)
                if not df.empty:
                    df['source_file'] = file_path
                    all_dfs.append(df)
            except Exception as e:
                self.logger.error(f"Error loading {file_path}: {e}")
        
        if not all_dfs:
            return pd.DataFrame()
        
        combined_df = pd.concat(all_dfs, ignore_index=True)
        self.logger.info(f"Aggregated {len(combined_df)} records from {len(all_dfs)} files")
        
        return combined_df
    
    def deduplicate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records based on product name and source."""
        if df.empty:
            return df
        
        original_count = len(df)
        
        # Define columns for duplicate detection
        duplicate_cols = ['name', 'source']
        if all(col in df.columns for col in duplicate_cols):
            # Keep the most recent record for duplicates
            if 'createdat' in df.columns:
                df_sorted = df.sort_values('createdat', ascending=False)
                deduped_df = df_sorted.drop_duplicates(subset=duplicate_cols, keep='first')
            else:
                deduped_df = df.drop_duplicates(subset=duplicate_cols, keep='first')
        else:
            deduped_df = df
        
        removed_count = original_count - len(deduped_df)
        self.logger.info(f"Removed {removed_count} duplicate records")
        
        return deduped_df.reset_index(drop=True)