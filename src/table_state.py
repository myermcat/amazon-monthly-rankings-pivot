"""
TableState class for managing pivot table metadata and structure.
Tracks column types, categories, months, and table schema.
"""

import json
import os
from typing import Dict, List, Set, Optional
from datetime import datetime


class TableState:
    """
    Manages the state and metadata of a pivot table.
    Tracks which columns are categories vs months, and maintains table structure.
    """
    
    def __init__(self, country: str, table_path: str = None):
        """
        Initialize TableState for a specific country.
        
        Args:
            country: Country code (e.g., 'US', 'CANADA')
            table_path: Path to existing table file (optional)
        """
        self.country = country
        self.table_path = table_path
        self.metadata_path = f"metadata/{country.lower()}_structure.json"
        
        # Table structure tracking
        self.categories: Set[str] = set()
        self.months: Set[str] = set()
        self.keywords: Set[str] = set()
        
        # Column type mapping
        self.column_types: Dict[str, str] = {}  # column_name -> 'category' or 'month'
        
        # Load existing state if available
        if table_path and os.path.exists(table_path):
            self.load_state()
    
    def add_category(self, category: str) -> None:
        """Add a new category to the table."""
        self.categories.add(category)
        self.column_types[category] = 'category'
        self._save_state()
    
    def add_month(self, month: str) -> None:
        """Add a new month to the table."""
        self.months.add(month)
        self.column_types[month] = 'month'
        self._save_state()
    
    def add_keywords(self, keywords: List[str]) -> None:
        """Add new keywords to the table."""
        self.keywords.update(keywords)
        self._save_state()
    
    def get_schema(self) -> Dict[str, any]:
        """Get the current table schema."""
        return {
            'country': self.country,
            'categories': sorted(list(self.categories)),
            'months': sorted(list(self.months)),
            'keyword_count': len(self.keywords),
            'column_types': self.column_types,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_categories(self) -> List[str]:
        """Get list of categories in alphabetical order."""
        return sorted(list(self.categories))
    
    def get_months(self) -> List[str]:
        """Get list of months in chronological order."""
        # Sort months by year and month
        def month_sort_key(month_str):
            if '-' in month_str:
                year, month = month_str.split('-', 1)
                month_order = ["January", "February", "March", "April", "May", "June", 
                              "July", "August", "September", "October", "November", "December"]
                try:
                    return (int(year), month_order.index(month))
                except (ValueError, IndexError):
                    return (9999, 999)
            return (9999, 999)
        
        return sorted(list(self.months), key=month_sort_key)
    
    def has_category(self, category: str) -> bool:
        """Check if category exists in table."""
        return category in self.categories
    
    def has_month(self, month: str) -> bool:
        """Check if month exists in table."""
        return month in self.months
    
    def get_column_type(self, column: str) -> Optional[str]:
        """Get the type of a column (category or month)."""
        return self.column_types.get(column)
    
    def _save_state(self) -> None:
        """Save current state to metadata file."""
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
        
        state_data = {
            'country': self.country,
            'categories': list(self.categories),
            'months': list(self.months),
            'keywords': list(self.keywords),
            'column_types': self.column_types,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.metadata_path, 'w') as f:
            json.dump(state_data, f, indent=2)
    
    def load_state(self) -> None:
        """Load state from metadata file."""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r') as f:
                    state_data = json.load(f)
                
                self.categories = set(state_data.get('categories', []))
                self.months = set(state_data.get('months', []))
                self.keywords = set(state_data.get('keywords', []))
                self.column_types = state_data.get('column_types', {})
                
            except (json.JSONDecodeError, FileNotFoundError):
                # If loading fails, start with empty state
                pass
    
    def get_diff(self, new_categories: Set[str], new_months: Set[str]) -> Dict[str, any]:
        """
        Get differences between current state and new data.
        
        Returns:
            Dict with 'new_categories', 'new_months', 'existing_categories', 'existing_months'
        """
        return {
            'new_categories': new_categories - self.categories,
            'new_months': new_months - self.months,
            'existing_categories': self.categories,
            'existing_months': self.months
        }
