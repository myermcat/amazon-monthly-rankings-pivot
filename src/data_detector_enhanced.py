"""
Enhanced DataDetector class with processing status integration.
Scans DATA folder and tracks what needs processing.
"""

import os
import glob
import re
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
from datetime import datetime


class DataDetector:
    """
    Detects and analyzes data structure in the DATA folder.
    Identifies countries, categories, and monthly files.
    Now integrates with processing status tracking.
    """
    
    def __init__(self, data_root: str = "DATA"):
        """
        Initialize DataDetector.
        
        Args:
            data_root: Path to the DATA folder
        """
        self.data_root = Path(data_root)
        self.countries: List[str] = []
        self.categories: Dict[str, List[str]] = {}
        self.monthly_files: Dict[str, Dict[str, List[str]]] = {}
        self.file_details: Dict[str, Dict[str, Dict[str, any]]] = {}  # country -> category -> file details
    
    def detect_countries(self) -> List[str]:
        """
        Detect all countries in the DATA folder.
        
        Returns:
            List of country names
        """
        if not self.data_root.exists():
            return []
        
        self.countries = [
            folder.name for folder in self.data_root.iterdir() 
            if folder.is_dir() and not folder.name.startswith('.')
        ]
        
        return self.countries
    
    def detect_categories(self, country: str = None) -> Dict[str, List[str]]:
        """
        Detect categories within a country or all countries.
        
        Args:
            country: Specific country to scan, or None for all
            
        Returns:
            Dict mapping country -> list of categories
        """
        if country:
            countries_to_scan = [country]
        else:
            countries_to_scan = self.countries
        
        for country_name in countries_to_scan:
            country_path = self.data_root / country_name
            if not country_path.exists():
                continue
            
            categories = [
                folder.name for folder in country_path.iterdir()
                if folder.is_dir() and not folder.name.startswith('.')
            ]
            
            self.categories[country_name] = categories
        
        return self.categories
    
    def detect_monthly_files(self, country: str = None, category: str = None) -> Dict[str, Dict[str, List[str]]]:
        """
        Detect monthly files within categories.
        
        Args:
            country: Specific country to scan, or None for all
            category: Specific category to scan, or None for all
            
        Returns:
            Dict mapping country -> category -> list of monthly files
        """
        if country:
            countries_to_scan = [country]
        else:
            countries_to_scan = self.countries
        
        for country_name in countries_to_scan:
            if country_name not in self.monthly_files:
                self.monthly_files[country_name] = {}
                self.file_details[country_name] = {}
            
            country_path = self.data_root / country_name
            if not country_path.exists():
                continue
            
            for category_folder in country_path.iterdir():
                if not category_folder.is_dir() or category_folder.name.startswith('.'):
                    continue
                
                if category and category_folder.name != category:
                    continue
                
                category_name = category_folder.name
                if category_name not in self.monthly_files[country_name]:
                    self.monthly_files[country_name][category_name] = []
                    self.file_details[country_name][category_name] = {}
                
                # Look for CSV files and collect details
                csv_files = list(category_folder.glob("*.csv"))
                self.monthly_files[country_name][category_name] = [f.name for f in csv_files]
                
                # Collect file details
                for csv_file in csv_files:
                    file_info = self._analyze_file(csv_file)
                    self.file_details[country_name][category_name][csv_file.name] = file_info
        
        return self.monthly_files
    
    def _analyze_file(self, file_path: Path) -> Dict[str, any]:
        """
        Analyze a CSV file to extract metadata.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Dictionary with file metadata
        """
        file_info = {
            'path': str(file_path),
            'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
            'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'parsed_date': None,
            'year': None,
            'month': None,
            'date_string': None
        }
        
        # Parse filename for date information
        year, month, date_string = self.parse_monthly_filename(file_path.name)
        if year and month:
            file_info.update({
                'parsed_date': True,
                'year': year,
                'month': month,
                'date_string': date_string
            })
        
        return file_info
    
    def parse_monthly_filename(self, filename: str) -> Tuple[str, str, str]:
        """
        Parse monthly filename to extract year, month, and date info.
        
        Args:
            filename: CSV filename
            
        Returns:
            Tuple of (year, month, full_date_string)
        """
        # Handle format: US_Top_search_terms_Simple_Month_2025_07_31.csv
        if filename.startswith(('US_', 'CA_')) and 'Simple_Month_' in filename:
            try:
                # Extract date part: 2025_07_31
                date_part = filename.split('Simple_Month_')[1].replace('.csv', '')
                year, month, day = date_part.split('_')
                
                # Convert month number to month name
                month_names = ["January", "February", "March", "April", "May", "June", 
                              "July", "August", "September", "October", "November", "December"]
                month_name = month_names[int(month) - 1]
                
                return year, month_name, f"{year}-{month_name}"
            except (IndexError, ValueError):
                pass
        
        # Handle format: 2025-July.csv
        elif re.match(r'\d{4}-[A-Za-z]+\.csv', filename):
            try:
                year_month = filename.replace('.csv', '')
                year, month = year_month.split('-')
                return year, month, year_month
            except ValueError:
                pass
        
        return None, None, None
    
    def get_monthly_files_by_date(self, country: str, category: str) -> List[Tuple[str, str, str]]:
        """
        Get monthly files sorted by date for a specific country/category.
        
        Args:
            country: Country name
            category: Category name
            
        Returns:
            List of (filename, year, month) tuples sorted by date
        """
        if country not in self.monthly_files or category not in self.monthly_files[country]:
            return []
        
        files_with_dates = []
        for filename in self.monthly_files[country][category]:
            year, month, date_string = self.parse_monthly_filename(filename)
            if year and month:
                files_with_dates.append((filename, year, month))
        
        # Sort by year, then by month
        month_order = ["January", "February", "March", "April", "May", "June", 
                      "July", "August", "September", "October", "November", "December"]
        
        files_with_dates.sort(key=lambda x: (int(x[1]), month_order.index(x[2])))
        return files_with_dates
    
    def get_latest_month(self, country: str, category: str) -> Tuple[str, str, str]:
        """
        Get the latest month available for a country/category.
        
        Args:
            country: Country name
            category: Category name
            
        Returns:
            Tuple of (filename, year, month) for the latest month
        """
        files_by_date = self.get_monthly_files_by_date(country, category)
        return files_by_date[-1] if files_by_date else (None, None, None)
    
    def get_file_details(self, country: str, category: str, filename: str) -> Optional[Dict[str, any]]:
        """
        Get detailed information about a specific file.
        
        Args:
            country: Country name
            category: Category name
            filename: CSV filename
            
        Returns:
            File details dictionary or None if not found
        """
        return self.file_details.get(country, {}).get(category, {}).get(filename)
    
    def get_category_summary(self, country: str, category: str) -> Dict[str, any]:
        """
        Get summary information for a specific category.
        
        Args:
            country: Country name
            category: Category name
            
        Returns:
            Category summary with file count, size, date range
        """
        if country not in self.file_details or category not in self.file_details[country]:
            return {}
        
        files = self.file_details[country][category]
        if not files:
            return {}
        
        total_size = sum(f['size_mb'] for f in files.values())
        date_files = [f for f in files.values() if f['parsed_date']]
        
        if date_files:
            dates = [f['date_string'] for f in date_files if f['date_string']]
            date_range = f"{min(dates)} to {max(dates)}" if dates else "Unknown"
        else:
            date_range = "Unknown"
        
        return {
            'file_count': len(files),
            'total_size_mb': round(total_size, 2),
            'date_range': date_range,
            'parsed_files': len(date_files),
            'unparsed_files': len(files) - len(date_files)
        }
    
    def scan_all_data(self) -> Dict[str, any]:
        """
        Perform complete scan of all data.
        
        Returns:
            Dict with complete data structure information
        """
        self.detect_countries()
        self.detect_categories()
        self.detect_monthly_files()
        
        return {
            'countries': self.countries,
            'categories': self.categories,
            'monthly_files': self.monthly_files,
            'file_details': self.file_details
        }
