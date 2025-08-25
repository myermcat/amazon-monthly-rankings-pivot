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
        
        # Reorder columns: Search Term, Categories, then Months
        self._reorder_columns()
        self.save_table()
        
        print(f"🎉 Successfully added category {category}!")
        print(f"   📁 Files processed: {len(processed_files)}")
        print(f"   🔑 New keywords added: {total_keywords_added}")
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
            print(f"📂 Loading existing table from {self.table_path}...")
            self.table = pd.read_csv(self.table_path)
            
            # Initialize TableState from the loaded table's columns
            self.table_state = TableState(country=self.country)
            
            # Infer categories and months from columns
            # Assuming category columns are non-date-like strings and month columns are date-like
            category_cols = []
            month_cols = []
            for col in self.table.columns:
                if col == "Search Term":  # Skip the index column
                    continue
                # Heuristic: if a column name can be parsed as a month, it's a month column
                # Otherwise, it's a category column (or other metadata)
                if self._is_month_column(col):
                    month_cols.append(col)
                else:
                    category_cols.append(col)
            
            for cat in category_cols:
                self.table_state.add_category(cat)
            for month in month_cols:
                self.table_state.add_month(month)

            print(f"📊 Loaded existing table with {len(self.table)} keywords.")
            print(f"🏷️ Categories in table state: {self.table_state.get_categories()}")
            print(f"📅 Months in table state: {self.table_state.get_months()}")
            self.table_state._save_state()
            
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

    def add_new_months(self, category: str, month_files: List[str]) -> pd.DataFrame:
        """
        Add new months to an existing category in the pivot table.
        
        Args:
            category: Category to expand with new months
            month_files: List of file paths for new month data
            
        Returns:
            Updated DataFrame
        """
        if self.table is None:
            raise ValueError("No table loaded. Create or load a table first.")
        
        if category not in self.table_state.get_categories():
            raise ValueError(f"Category '{category}' not found in table. Add category first.")
        
        print(f"📅 Expanding category '{category}' with new months...")
        
        new_months_added = 0
        processed_files = []
        
        for file_path in month_files:
            try:
                # Extract month from filename
                filename = Path(file_path).name
                month_match = self._extract_month_from_filename(filename)
                
                if not month_match:
                    print(f"⚠️  Could not extract month from filename: {filename}")
                    continue
                
                month_name = month_match
                
                # Check if month already exists
                if month_name in self.table_state.get_months():
                    print(f"⏭️  Month {month_name} already exists, skipping")
                    continue
                
                print(f"  ➕ Adding month: {month_name}")
                
                # Import month data
                month_data = self._import_month_data(file_path, category)
                
                # Add new month column
                self.table[month_name] = 0  # Initialize with 0s
                
                # Populate data for existing keywords
                for search_term, rank in month_data.items():
                    if search_term in self.table['Search Term'].values:
                        # Find the row index
                        row_idx = self.table[self.table['Search Term'] == search_term].index[0]
                        self.table.loc[row_idx, month_name] = rank
                
                # Add month to table state
                self.table_state.add_month(month_name)
                new_months_added += 1
                processed_files.append(file_path)
                
                print(f"    ✅ Added {month_name} with {len(month_data)} data points")
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
                continue
        
        if new_months_added > 0:
            # Reorder columns and save
            self._reorder_columns()
            self.save_table()
            
            print(f"🎉 Successfully added {new_months_added} new months to category '{category}'!")
            print(f"   📁 Files processed: {len(processed_files)}")
            print(f"   📊 Table dimensions: {self.table.shape}")
        else:
            print("ℹ️  No new months were added")
        
        return self.table
    
    def expand_monthly_columns(self, category: str) -> pd.DataFrame:
        """
        Automatically detect and add new months for a category from available files.
        
        Args:
            category: Category to expand with new months
            
        Returns:
            Updated DataFrame
        """
        if self.table is None:
            raise ValueError("No table loaded. Create or load a table first.")
        
        print(f"🔍 Auto-expanding monthly columns for category '{category}'...")
        
        # Get available month files for this category
        available_files = self.data_detector.get_category_files(self.country, category)
        
        if not available_files:
            print(f"⚠️  No files found for category '{category}'")
            return self.table
        
        # Filter for month files (not combined files)
        month_files = [f for f in available_files if self._is_monthly_file(f)]
        
        if not month_files:
            print(f"⚠️  No monthly files found for category '{category}'")
            return self.table
        
        print(f"📁 Found {len(month_files)} monthly files")
        
        # Add new months
        return self.add_new_months(category, month_files)
    
    def analyze_changes(self, new_files: List[str] = None) -> Dict[str, any]:
        """
        Analyze what's new by comparing available files with current table.
        
        Args:
            new_files: Optional list of specific files to analyze, or None to scan all
            
        Returns:
            Dictionary with analysis results
        """
        if self.table is None:
            return {"error": "No table loaded"}
        
        print(f"🔍 Analyzing changes for {self.country}...")
        
        # Get current table state
        current_categories = set(self.table_state.get_categories())
        current_months = set(self.table_state.get_months())
        
        # Scan for available data
        if new_files:
            available_files = new_files
        else:
            # Auto-scan all available data
            available_files = []
            for category in current_categories:
                category_files = self.data_detector.get_category_files(self.country, category)
                available_files.extend(category_files)
        
        # Analyze each file
        new_months = set()
        new_categories = set()
        new_keywords = set()
        file_analysis = {}
        
        for file_path in available_files:
            try:
                filename = Path(file_path).name
                category = self._extract_category_from_path(file_path)
                
                if self._is_monthly_file(file_path):
                    # Monthly file
                    month_name = self._extract_month_from_filename(filename)
                    if month_name and month_name not in current_months:
                        new_months.add(month_name)
                        if month_name not in file_analysis:
                            file_analysis[month_name] = {'type': 'month', 'files': [], 'category': category}
                        file_analysis[month_name]['files'].append(file_path)
                else:
                    # Combined file - potential new category
                    if category and category not in current_categories:
                        new_categories.add(category)
                        if category not in file_analysis:
                            file_analysis[category] = {'type': 'category', 'files': [], 'months': []}
                        file_analysis[category]['files'].append(file_path)
                        
                        # Extract months from combined file
                        combined_months = self._extract_months_from_combined_file(file_path)
                        for month in combined_months:
                            if month not in current_months:
                                new_months.add(month)
                                file_analysis[category]['months'].append(month)
                
            except Exception as e:
                print(f"⚠️  Error analyzing {file_path}: {e}")
                continue
        
        # Count potential new keywords
        for file_path in available_files:
            try:
                if self._is_monthly_file(file_path):
                    month_data = self._import_month_data(file_path, "unknown")
                    new_keywords.update(set(month_data.keys()) - set(self.table['Search Term'].values))
            except:
                continue
        
        analysis_result = {
            'new_months': sorted(list(new_months)),
            'new_categories': sorted(list(new_categories)),
            'new_keywords_count': len(new_keywords),
            'file_analysis': file_analysis,
            'current_state': {
                'categories': sorted(list(current_categories)),
                'months': sorted(list(current_months)),
                'keywords': len(self.table)
            },
            'recommendations': self._generate_update_recommendations(new_months, new_categories, new_keywords)
        }
        
        print(f"✅ Analysis complete!")
        print(f"   📅 New months: {len(new_months)}")
        print(f"   🏷️  New categories: {len(new_categories)}")
        print(f"   🔑 New keywords: {len(new_keywords)}")
        
        return analysis_result
    
    def generate_update_report(self, analysis: Dict[str, any] = None) -> str:
        """
        Generate a human-readable update report.
        
        Args:
            analysis: Analysis result from analyze_changes(), or None to auto-analyze
            
        Returns:
            Formatted report string
        """
        if analysis is None:
            analysis = self.analyze_changes()
        
        if 'error' in analysis:
            return f"❌ Error: {analysis['error']}"
        
        report = []
        report.append("📊 UPDATE ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Country: {self.country}")
        report.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Current state
        report.append("🏠 CURRENT STATE:")
        report.append(f"  Categories: {', '.join(analysis['current_state']['categories'])}")
        report.append(f"  Months: {len(analysis['current_state']['months'])} (from {analysis['current_state']['months'][0]} to {analysis['current_state']['months'][-1]})")
        report.append(f"  Keywords: {analysis['current_state']['keywords']:,}")
        report.append("")
        
        # New data available
        report.append("🆕 NEW DATA AVAILABLE:")
        
        if analysis['new_months']:
            report.append(f"  📅 New Months ({len(analysis['new_months'])}):")
            for month in analysis['new_months']:
                report.append(f"    • {month}")
        else:
            report.append("  📅 New Months: None")
        
        if analysis['new_categories']:
            report.append(f"  🏷️  New Categories ({len(analysis['new_categories'])}):")
            for category in analysis['new_categories']:
                report.append(f"    • {category}")
        else:
            report.append("  🏷️  New Categories: None")
        
        if analysis['new_keywords_count'] > 0:
            report.append(f"  🔑 New Keywords: {analysis['new_keywords_count']:,}")
        else:
            report.append("  🔑 New Keywords: None")
        
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        for rec in analysis['recommendations']:
            report.append(f"  • {rec}")
        
        report.append("")
        report.append("🔧 NEXT STEPS:")
        if analysis['new_months'] or analysis['new_categories']:
            report.append("  1. Review the analysis above")
            report.append("  2. Choose what to add (months, categories, or both)")
            report.append("  3. Run the appropriate update method")
        else:
            report.append("  ✅ No updates needed - table is current!")
        
        return "\n".join(report)
    
    def prompt_user_for_updates(self, analysis: Dict[str, any] = None) -> Dict[str, any]:
        """
        Interactive prompt system for user decisions on updates.
        
        Args:
            analysis: Analysis result from analyze_changes(), or None to auto-analyze
            
        Returns:
            Dictionary with user decisions
        """
        if analysis is None:
            analysis = self.analyze_changes()
        
        if 'error' in analysis:
            print(f"❌ Error: {analysis['error']}")
            return {}
        
        # Show current state and what's new
        print("\n" + "="*60)
        print("🎮 UPDATE DECISION INTERFACE")
        print("="*60)
        
        # Current state summary
        print(f"🏠 Current Table State:")
        print(f"  Country: {self.country}")
        print(f"  Categories: {', '.join(analysis['current_state']['categories'])}")
        print(f"  Months: {len(analysis['current_state']['months'])} (from {analysis['current_state']['months'][0]} to {analysis['current_state']['months'][-1]})")
        print(f"  Keywords: {analysis['current_state']['keywords']:,}")
        
        # What's new
        print(f"\n🆕 New Data Available:")
        if analysis['new_months']:
            print(f"  📅 New Months ({len(analysis['new_months'])}): {', '.join(analysis['new_months'])}")
        if analysis['new_categories']:
            print(f"  🏷️  New Categories ({len(analysis['new_categories'])}): {', '.join(analysis['new_categories'])}")
        if analysis['new_keywords_count'] > 0:
            print(f"  🔑 New Keywords: {analysis['new_keywords_count']:,}")
        
        if not analysis['new_months'] and not analysis['new_categories']:
            print("  ✅ No new data detected - table is current!")
            return {'action': 'none', 'reason': 'no_updates_needed'}
        
        # User choices
        print(f"\n🔧 What would you like to do?")
        print(f"  1. Add new months only")
        print(f"  2. Add new categories only") 
        print(f"  3. Add both months and categories")
        print(f"  4. Skip updates for now")
        print(f"  5. View detailed analysis report")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == '1' and analysis['new_months']:
                    return self._handle_month_only_update(analysis)
                elif choice == '2' and analysis['new_categories']:
                    return self._handle_category_only_update(analysis)
                elif choice == '3' and (analysis['new_months'] or analysis['new_categories']):
                    return self._handle_comprehensive_update(analysis)
                elif choice == '4':
                    return {'action': 'skip', 'reason': 'user_choice'}
                elif choice == '5':
                    print("\n" + self.generate_update_report(analysis))
                    continue  # Show menu again
                else:
                    print("❌ Invalid choice or no data available for that option. Please try again.")
                    continue
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Update cancelled by user.")
                return {'action': 'cancelled', 'reason': 'user_interrupt'}
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
    
    def _handle_month_only_update(self, analysis: Dict[str, any]) -> Dict[str, any]:
        """Handle user choice to add months only."""
        print(f"\n📅 Adding new months only...")
        
        if not analysis['new_months']:
            return {'action': 'error', 'reason': 'no_new_months'}
        
        # Show which months will be added
        print(f"  📅 Months to add: {', '.join(analysis['new_months'])}")
        
        # Confirm action
        if self._confirm_action("Add these new months?"):
            return {
                'action': 'update_months',
                'months': analysis['new_months'],
                'categories': [],
                'reason': 'user_confirmed_months_only'
            }
        else:
            return {'action': 'cancelled', 'reason': 'user_declined'}
    
    def _handle_category_only_update(self, analysis: Dict[str, any]) -> Dict[str, any]:
        """Handle user choice to add categories only."""
        print(f"\n🏷️  Adding new categories only...")
        
        if not analysis['new_categories']:
            return {'action': 'error', 'reason': 'no_new_categories'}
        
        # Show which categories will be added
        print(f"  🏷️  Categories to add: {', '.join(analysis['new_categories'])}")
        
        # Confirm action
        if self._confirm_action("Add these new categories?"):
            return {
                'action': 'update_categories',
                'months': [],
                'categories': analysis['new_categories'],
                'reason': 'user_confirmed_categories_only'
            }
        else:
            return {'action': 'cancelled', 'reason': 'user_declined'}
    
    def _handle_comprehensive_update(self, analysis: Dict[str, any]) -> Dict[str, any]:
        """Handle user choice to add both months and categories."""
        print(f"\n🚀 Adding both new months and categories...")
        
        months_to_add = analysis['new_months']
        categories_to_add = analysis['new_categories']
        
        if months_to_add:
            print(f"  📅 Months to add: {', '.join(months_to_add)}")
        if categories_to_add:
            print(f"  🏷️  Categories to add: {', '.join(categories_to_add)}")
        
        # Confirm action
        if self._confirm_action("Add all this new data?"):
            return {
                'action': 'update_all',
                'months': months_to_add,
                'categories': categories_to_add,
                'reason': 'user_confirmed_comprehensive'
            }
        else:
            return {'action': 'cancelled', 'reason': 'user_declined'}
    
    def _confirm_action(self, message: str) -> bool:
        """Ask user to confirm an action."""
        while True:
            try:
                response = input(f"\n{message} (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no.")
            except KeyboardInterrupt:
                print("\n⚠️  Action cancelled.")
                return False
    
    def execute_user_decision(self, decision: Dict[str, any]) -> bool:
        """
        Execute the user's decision on updates.
        
        Args:
            decision: Decision dictionary from prompt_user_for_updates()
            
        Returns:
            True if successful, False otherwise
        """
        if not decision or 'action' not in decision:
            print("❌ No valid decision to execute")
            return False
        
        action = decision['action']
        
        if action == 'none':
            print("✅ No updates needed - table is current!")
            return True
        elif action == 'skip':
            print("⏭️  Updates skipped by user")
            return True
        elif action == 'cancelled':
            print("❌ Update cancelled")
            return False
        elif action == 'error':
            print(f"❌ Error: {decision.get('reason', 'unknown')}")
            return False
        
        print(f"\n🚀 Executing user decision: {action}")
        
        try:
            if action == 'update_months':
                return self._execute_month_update(decision)
            elif action == 'update_categories':
                return self._execute_category_update(decision)
            elif action == 'update_all':
                return self._execute_comprehensive_update(decision)
            else:
                print(f"❌ Unknown action: {action}")
                return False
                
        except Exception as e:
            print(f"❌ Error executing update: {e}")
            return False
    
    def _execute_month_update(self, decision: Dict[str, any]) -> bool:
        """Execute month-only update."""
        months = decision.get('months', [])
        if not months:
            print("⚠️  No months specified for update")
            return False
        
        print(f"📅 Adding {len(months)} new months...")
        
        # For now, we'll need to implement month addition logic
        # This would integrate with the existing month expansion methods
        print("⚠️  Month update execution not yet implemented")
        return False
    
    def _execute_category_update(self, decision: Dict[str, any]) -> bool:
        """Execute category-only update."""
        categories = decision.get('categories', [])
        if not categories:
            print("⚠️  No categories specified for update")
            return False
        
        print(f"🏷️  Adding {len(categories)} new categories...")
        
        # For now, we'll need to implement category addition logic
        # This would integrate with the existing category expansion methods
        print("⚠️  Category update execution not yet implemented")
        return False
    
    def _execute_comprehensive_update(self, decision: Dict[str, any]) -> bool:
        """Execute comprehensive update (both months and categories)."""
        months = decision.get('months', [])
        categories = decision.get('categories', [])
        
        print(f"🚀 Executing comprehensive update...")
        print(f"  📅 Months: {len(months)}")
        print(f"  🏷️  Categories: {len(categories)}")
        
        # For now, we'll need to implement comprehensive update logic
        print("⚠️  Comprehensive update execution not yet implemented")
        return False

    def _extract_category_from_path(self, file_path: str) -> Optional[str]:
        """Extract category name from file path."""
        try:
            path_parts = Path(file_path).parts
            # Look for category in path: DATA/country/category/filename
            if len(path_parts) >= 3:
                return path_parts[-2]  # Second-to-last part
        except:
            pass
        return None
    
    def _extract_months_from_combined_file(self, file_path: str) -> List[str]:
        """Extract month names from a combined file by analyzing column headers."""
        try:
            df = pd.read_csv(file_path, skiprows=1)  # Skip metadata row
            months = []
            
            for col in df.columns:
                if col != 'Search Term' and self._is_month_column(col):
                    months.append(col)
            
            return months
        except:
            return []
    
    def _generate_update_recommendations(self, new_months: Set[str], new_categories: Set[str], new_keywords: Set[str]) -> List[str]:
        """Generate intelligent update recommendations."""
        recommendations = []

        if new_months and new_categories:
            recommendations.append("Add both new months and new categories for comprehensive update")
        elif new_months:
            recommendations.append("Add new months to expand temporal coverage")
        elif new_categories:
            recommendations.append("Add new categories to expand category coverage")
        
        if new_keywords:
            recommendations.append(f"Update will add {len(new_keywords):,} new keywords to the table")
        
        if not new_months and not new_categories:
            recommendations.append("No new data detected - table is current")
        
        return recommendations

    def _extract_month_from_filename(self, filename: str) -> Optional[str]:
        """
        Extract month name from filename like 'US_Top_search_terms_Simple_Month_2025_07_31.csv'
        Returns format like '2025-July'
        """
        try:
            # Pattern: US_Top_search_terms_Simple_Month_YYYY_MM_DD.csv
            parts = filename.split('_')
            if len(parts) >= 6:
                year = parts[5]
                month_num = int(parts[6])
                
                month_names = [
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'
                ]
                
                month_name = month_names[month_num - 1]
                return f"{year}-{month_name}"
        except (ValueError, IndexError):
            pass
        
        return None
    
    def _is_monthly_file(self, file_path: str) -> bool:
        """Check if file is a monthly data file (not a combined file)."""
        filename = Path(file_path).name
        # Monthly files have the pattern: YYYY_MM_DD
        return '_202' in filename and filename.count('_') >= 6
    
    def _is_month_column(self, col_name: str) -> bool:
        """Heuristic to determine if a column name represents a month."""
        # Check for YYYY-Month format
        if '-' in col_name:
            parts = col_name.split('-')
            if len(parts) == 2 and parts[0].isdigit():
                year = int(parts[0])
                month_name = parts[1]
                month_order = ["January", "February", "March", "April", "May", "June", 
                              "July", "August", "September", "October", "November", "December"]
                return month_name in month_order
        return False
    
    def _import_month_data(self, file_path: str, category: str) -> Dict[str, int]:
        """
        Import monthly data from a CSV file.
        Returns dict mapping search terms to rankings.
        """
        try:
            # Read CSV starting from row 2 (skip metadata row, use row 1 as headers)
            df = pd.read_csv(file_path, skiprows=1)
            
            # Find required columns
            search_term_col = None
            rank_col = None
            
            for col in df.columns:
                if "Search Term" in col:
                    search_term_col = col
                if "Search Frequency Rank" in col:
                    rank_col = col
            
            if not search_term_col or not rank_col:
                raise ValueError(f"Required columns not found in {file_path}")
            
            # Create mapping
            data = {}
            for _, row in df.iterrows():
                search_term = row[search_term_col]
                rank = row[rank_col]
                
                # Convert rank to int, handle NaN
                if pd.notna(rank):
                    try:
                        data[search_term] = int(rank)
                    except (ValueError, TypeError):
                        continue
            
            return data
            
        except Exception as e:
            print(f"❌ Error importing month data from {file_path}: {e}")
            return {}

    def _reorder_columns(self):
        """Reorder columns to: Search Term, Categories, then Months."""
        if self.table is None:
            return

        # Get column lists
        search_term_col = 'Search Term'
        category_cols = [col for col in self.table.columns if col in self.table_state.get_categories()]
        month_cols = [col for col in self.table.columns if '-' in col]

        # Sort months chronologically
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_cols.sort(key=lambda x: (int(x.split('-')[0]), month_order.index(x.split('-')[1])))

        # Create new column order
        new_order = [search_term_col] + category_cols + month_cols
        self.table = self.table[new_order]
        print(f'✅ Columns reordered: {len(category_cols)} categories, {len(month_cols)} months')
