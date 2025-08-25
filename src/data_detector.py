"""
DataDetector class for scanning and detecting data structure.
Scans DATA folder for countries, categories, and monthly files.
"""

import os
import glob
import re
from typing import Dict, List, Set, Tuple
from pathlib import Path


class DataDetector:
    """
    Detects and analyzes data structure in the DATA folder.
    Identifies countries, categories, and monthly files.
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
                
                # Look for CSV files
                csv_files = list(category_folder.glob("*.csv"))
                self.monthly_files[country_name][category_name] = [f.name for f in csv_files]
        
        return self.monthly_files
    
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
            'monthly_files': self.monthly_files
        }
