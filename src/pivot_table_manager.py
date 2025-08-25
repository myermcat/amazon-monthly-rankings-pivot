"""
PivotTableManager class for managing multi-dimensional pivot tables.
Handles table creation, expansion, and data merging.
"""

import pandas as pd
import os
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path

from table_state import TableState
from data_detector import DataDetector


class PivotTableManager:
    """
    Manages the creation and expansion of multi-dimensional pivot tables.
    Handles merging categories, months, and keywords intelligently.
    """
    
    def __init__(self, country: str, output_dir: str = "outputs"):
        """
        Initialize PivotTableManager for a specific country.
        
        Args:
            country: Country code (e.g., 'US', 'CANADA')
            output_dir: Directory for output files
        """
        self.country = country
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.table_state = TableState(country)
        self.data_detector = DataDetector()
        
        # Table paths
        self.table_path = self.output_dir / f"{country.lower()}_pivot_table.csv"
        self.metadata_dir = self.output_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        
        # Current table
        self.table: Optional[pd.DataFrame] = None
        
        # Load existing table if available
        if self.table_path.exists():
            self.load_table()
    
    def get_structure(self) -> Dict[str, any]:
        """Get current table structure."""
        return self.table_state.get_schema()
    
    def get_categories(self) -> List[str]:
        """Get list of categories in the table."""
        return self.table_state.get_categories()
    
    def get_months(self) -> List[str]:
        """Get list of months in the table."""
        return self.table_state.get_months()
    
    def create_from_anchor(self, anchor_category: str, anchor_file_path: str) -> pd.DataFrame:
        """
        Create initial table from an anchor category file.
        
        Args:
            anchor_category: Category name to use as anchor
            anchor_file_path: Path to the anchor CSV file
            
        Returns:
            Created DataFrame
        """
        print(f"Creating pivot table from anchor category: {anchor_category}")
        
        # Load anchor data
        anchor_df = pd.read_csv(anchor_file_path)
        
        # Extract search terms and monthly data
        if 'Search Term' in anchor_df.columns:
            search_terms = anchor_df['Search Term'].tolist()
        else:
            # Fallback: use first column as search terms
            search_terms = anchor_df.iloc[:, 0].tolist()
        
        # Create base table
        self.table = pd.DataFrame({'Search Term': search_terms})
        
        # Add category presence column
        self.table[anchor_category] = 1
        
        # Add monthly data columns
        monthly_columns = [col for col in anchor_df.columns if col != 'Search Term']
        for col in monthly_columns:
            self.table[col] = anchor_df[col].values
            self.table_state.add_month(col)
        
        # Update table state
        self.table_state.add_category(anchor_category)
        self.table_state.add_keywords(search_terms)
        
        # Save table
        self.save_table()
        
        print(f"Created table with {len(self.table)} keywords and {len(monthly_columns)} months")
        return self.table
    
    def add_category(self, category: str, category_files: List[str]) -> pd.DataFrame:
        """
        Add a new category to the existing table.
        
        Args:
            category: Category name to add
            category_files: List of monthly CSV files for the category
            
        Returns:
            Updated DataFrame
        """
        if not self.table is not None:
            raise ValueError("No existing table. Create table first using create_from_anchor().")
        
        print(f"Adding category: {category}")
        
        # Add category presence column
        self.table[category] = 0  # Initialize with 0s
        
        # Process each monthly file
        for file_path in category_files:
            if not os.path.exists(file_path):
                continue
            
            try:
                # Load category data
                cat_df = pd.read_csv(file_path)
                
                # Extract month info from filename
                filename = os.path.basename(file_path)
                year, month, date_string = self.data_detector.parse_monthly_filename(filename)
                
                if not date_string:
                    continue
                
                # Add month column if new
                if date_string not in self.table.columns:
                    self.table[date_string] = 0
                    self.table_state.add_month(date_string)
                
                # Update category presence and monthly data
                if 'Search Term' in cat_df.columns:
                    for _, row in cat_df.iterrows():
                        search_term = row['Search Term']
                        ranking = row.get('Search Frequency Rank', 0)
                        
                        # Find matching row in main table
                        mask = self.table['Search Term'] == search_term
                        if mask.any():
                            # Update existing keyword
                            self.table.loc[mask, category] = 1
                            self.table.loc[mask, date_string] = ranking
                        else:
                            # Add new keyword
                            new_row = pd.DataFrame({
                                'Search Term': [search_term],
                                category: [1],
                                date_string: [ranking]
                            })
                            # Fill other columns with 0s
                            for col in self.table.columns:
                                if col not in ['Search Term', category, date_string]:
                                    new_row[col] = 0
                            
                            self.table = pd.concat([self.table, new_row], ignore_index=True)
                            self.table_state.add_keywords([search_term])
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # Update table state
        self.table_state.add_category(category)
        
        # Save updated table
        self.save_table()
        
        print(f"Added category {category}. Table now has {len(self.table)} keywords")
        return self.table
    
    def add_months(self, category: str, new_month_files: List[str]) -> pd.DataFrame:
        """
        Add new months to an existing category.
        
        Args:
            category: Category name
            new_month_files: List of new monthly CSV files
            
        Returns:
            Updated DataFrame
        """
        if not self.table is not None:
            raise ValueError("No existing table.")
        
        if category not in self.table_state.get_categories():
            raise ValueError(f"Category {category} not found in table.")
        
        print(f"Adding new months to category: {category}")
        
        for file_path in new_month_files:
            if not os.path.exists(file_path):
                continue
            
            try:
                # Load month data
                month_df = pd.read_csv(file_path)
                
                # Extract month info
                filename = os.path.basename(file_path)
                year, month, date_string = self.data_detector.parse_monthly_filename(filename)
                
                if not date_string or date_string in self.table.columns:
                    continue
                
                # Add new month column
                self.table[date_string] = 0
                self.table_state.add_month(date_string)
                
                # Update data for existing keywords
                if 'Search Term' in month_df.columns:
                    for _, row in month_df.iterrows():
                        search_term = row['Search Term']
                        ranking = row.get('Search Frequency Rank', 0)
                        
                        mask = self.table['Search Term'] == search_term
                        if mask.any():
                            self.table.loc[mask, date_string] = ranking
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # Save updated table
        self.save_table()
        
        print(f"Added new months. Table now has {len(self.table_state.get_months())} months")
        return self.table
    
    def save_table(self) -> None:
        """Save current table to CSV file."""
        if self.table is not None:
            self.table.to_csv(self.table_path, index=False)
            self.table_state._save_state()
            print(f"Table saved to {self.table_path}")
    
    def load_table(self) -> pd.DataFrame:
        """Load existing table from CSV file."""
        if self.table_path.exists():
            self.table = pd.read_csv(self.table_path)
            
            # Update table state from loaded table
            for col in self.table.columns:
                if col != 'Search Term':
                    if col in self.table_state.get_categories():
                        self.table_state.add_category(col)
                    else:
                        self.table_state.add_month(col)
            
            print(f"Loaded existing table with {len(self.table)} keywords")
            return self.table
        else:
            print("No existing table found")
            return None
    
    def get_table_info(self) -> Dict[str, any]:
        """Get comprehensive information about the current table."""
        if self.table is None:
            return {"status": "No table loaded"}
        
        return {
            "status": "Table loaded",
            "file_path": str(self.table_path),
            "dimensions": self.table.shape,
            "categories": self.table_state.get_categories(),
            "months": self.table_state.get_months(),
            "keyword_count": len(self.table),
            "last_updated": self.table_state.get_schema()["last_updated"]
        }
