"""
Enhanced PivotTableManager with full table creation and data import functionality.
Handles creating pivot tables from anchor categories and expanding with new data.
"""

import pandas as pd
import os
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
import json

from table_state_enhanced import TableState
from data_detector_enhanced import DataDetector


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
        print(f"🚀 Creating pivot table from anchor category: {anchor_category}")
        
        if not os.path.exists(anchor_file_path):
            raise FileNotFoundError(f"Anchor file not found: {anchor_file_path}")
        
        # Load anchor data
        print(f"📁 Loading anchor data from: {anchor_file_path}")
        anchor_df = pd.read_csv(anchor_file_path)
        
        # Extract search terms and monthly data
        if 'Search Term' in anchor_df.columns:
            search_terms = anchor_df['Search Term'].tolist()
            print(f"✅ Found {len(search_terms)} search terms")
        else:
            # Fallback: use first column as search terms
            search_terms = anchor_df.iloc[:, 0].tolist()
            print(f"⚠️  Using first column as search terms: {len(search_terms)} found")
        
        # Create base table
        self.table = pd.DataFrame({'Search Term': search_terms})
        
        # Add category presence column
        self.table[anchor_category] = 1
        print(f"✅ Added category presence column: {anchor_category}")
        
        # Add monthly data columns
        monthly_columns = [col for col in anchor_df.columns if col != 'Search Term']
        print(f"📅 Adding {len(monthly_columns)} monthly columns")
        
        for col in monthly_columns:
            self.table[col] = anchor_df[col].values
            self.table_state.add_month(col)
            print(f"  ✅ Added month: {col}")
        
        # Update table state
        self.table_state.add_category(anchor_category)
        self.table_state.add_keywords(search_terms)
        
        # Mark category as processed
        self.table_state.mark_category_processed(
            anchor_category, 
            [os.path.basename(anchor_file_path)], 
            len(search_terms)
        )
        
        # Save table
        self.save_table()
        
        print(f"🎉 Successfully created pivot table!")
        print(f"   📊 Dimensions: {self.table.shape}")
        print(f"   🔑 Keywords: {len(search_terms)}")
        print(f"   📅 Months: {len(monthly_columns)}")
        print(f"   🏷️  Categories: 1 ({anchor_category})")
        
        return self.table
    
    def import_category_data(self, category: str, csv_file_path: str) -> Dict[str, any]:
        """
        Import data from a category CSV file.
        
        Args:
            category: Category name
            csv_file_path: Path to CSV file
            
        Returns:
            Dictionary with import results
        """
        print(f"📥 Importing data for category: {category}")
        
        if not os.path.exists(csv_file_path):
            return {"success": False, "error": "File not found"}
        
        try:
            # Load CSV data (skip metadata row)
            df = pd.read_csv(csv_file_path, skiprows=1)
            
            # Extract search terms and rankings
            if 'Search Term' not in df.columns:
                return {"success": False, "error": "No 'Search Term' column found"}
            
            if 'Search Frequency Rank' not in df.columns:
                return {"success": False, "error": "No 'Search Frequency Rank' column found"}
            
            # Create data dictionary
            data = {}
            for _, row in df.iterrows():
                search_term = row['Search Term']
                ranking = row['Search Frequency Rank']
                data[search_term] = ranking
            
            print(f"✅ Imported {len(data)} keywords from {category}")
            
            return {
                "success": True,
                "category": category,
                "keyword_count": len(data),
                "data": data,
                "file_path": csv_file_path
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_category_to_table(self, category: str, category_files: List[str]) -> pd.DataFrame:
        """
        Add a new category to the existing table.
        
        Args:
            category: Category name to add
            category_files: List of monthly CSV files for the category
            
        Returns:
            Updated DataFrame
        """
        if self.table is None:
            raise ValueError("No existing table. Create table first using create_from_anchor().")
        
        print(f"➕ Adding category: {category}")
        
        # Add category presence column
        self.table[category] = 0  # Initialize with 0s
        print(f"✅ Added category column: {category}")
        
        # Process each monthly file
        processed_files = []
        total_keywords_added = 0
        
        for file_path in category_files:
            if not os.path.exists(file_path):
                print(f"⚠️  File not found: {file_path}")
                continue
            
            try:
                # Import data from file
                import_result = self.import_category_data(category, file_path)
                
                if not import_result["success"]:
                    print(f"❌ Failed to import {file_path}: {import_result['error']}")
                    continue
                
                # Extract month info from filename
                filename = os.path.basename(file_path)
                year, month, date_string = self.data_detector.parse_monthly_filename(filename)
                
                if not date_string:
                    print(f"⚠️  Could not parse date from filename: {filename}")
                    continue
                
                # Add month column if new
                if date_string not in self.table.columns:
                    self.table[date_string] = 0
                    self.table_state.add_month(date_string)
                    print(f"✅ Added new month column: {date_string}")
                
                # Update category presence and monthly data
                data = import_result["data"]
                new_keywords = 0
                
                for search_term, ranking in data.items():
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
                        new_keywords += 1
                        self.table_state.add_keywords([search_term])
                
                processed_files.append(file_path)
                total_keywords_added += new_keywords
                
                if new_keywords > 0:
                    print(f"  ➕ Added {new_keywords} new keywords for {date_string}")
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
                continue
        
        # Update table state
        self.table_state.add_category(category)
        self.table_state.mark_category_processed(
            category, 
            processed_files, 
            len(self.table[self.table[category] == 1])
        )
        
        # Save updated table
        self.save_table()
        
        print(f"🎉 Successfully added category {category}!")
        print(f"   📁 Files processed: {len(processed_files)}")
        print(f"   �� New keywords added: {total_keywords_added}")
        print(f"   📊 Table dimensions: {self.table.shape}")
        
        return self.table
    
    def save_table(self) -> None:
        """Save current table to CSV file."""
        if self.table is not None:
            self.table.to_csv(self.table_path, index=False)
            self.table_state._save_state()
            print(f"💾 Table saved to {self.table_path}")
    
    def load_table(self) -> pd.DataFrame:
        """Load existing table from CSV file."""
        if self.table_path.exists():
            self.table = pd.read_csv(self.table_path)
            
            # Update table state from loaded table (sync categories and months)
            for col in self.table.columns:
                if col != 'Search Term':
                    if col in self.table_state.get_categories():
                        self.table_state.add_category(col)
                    else:
                        self.table_state.add_month(col)
            
            print(f"📂 Loaded existing table with {len(self.table)} keywords")
            return self.table
        else:
            print("📂 No existing table found")
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
    
    def get_processing_summary(self) -> Dict[str, any]:
        """Get processing status summary."""
        return self.table_state.get_processing_summary()
