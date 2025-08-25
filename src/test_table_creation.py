#!/usr/bin/env python3
"""
Test script for table creation functionality.
Tests creating pivot tables from anchor categories.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pivot_table_manager_enhanced import PivotTableManager


def test_create_from_anchor():
    """Test creating a table from an anchor category."""
    print("🧪 Testing Table Creation from Anchor...")
    
    # Test with US Beauty anchor
    print("\n1. Testing US Beauty anchor...")
    us_manager = PivotTableManager("US")
    
    # Check if we have an existing table
    if us_manager.table is not None:
        print("  📂 Found existing table, loading...")
        info = us_manager.get_table_info()
        print(f"  📊 Table info: {info}")
    else:
        print("  🆕 No existing table, will create new one")
    
    # Test processing summary
    summary = us_manager.get_processing_summary()
    print(f"  📈 Processing summary: {summary}")
    
    print("✅ US table creation test completed\n")
    
    # Test with Canada Beauty anchor
    print("2. Testing Canada Beauty anchor...")
    canada_manager = PivotTableManager("CANADA")
    
    # Check if we have an existing table
    if canada_manager.table is not None:
        print("  📂 Found existing table, loading...")
        info = canada_manager.get_table_info()
        print(f"  📊 Table info: {info}")
    else:
        print("  🆕 No existing table, will create new one")
    
    # Test processing summary
    summary = canada_manager.get_processing_summary()
    print(f"  📈 Processing summary: {summary}")
    
    print("✅ Canada table creation test completed\n")


def test_anchor_file_analysis():
    """Test analyzing the anchor files we have."""
    print("🧪 Testing Anchor File Analysis...")
    
    # Check what anchor files we have
    existing_tables_dir = Path("../existing_tables")
    
    if existing_tables_dir.exists():
        anchor_files = list(existing_tables_dir.glob("*.csv"))
        print(f"  📁 Found {len(anchor_files)} anchor files:")
        
        for file_path in anchor_files:
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            print(f"    📄 {file_path.name}: {file_size:.1f} MB")
            
            # Try to read the file structure
            try:
                df = pd.read_csv(file_path, nrows=5)  # Just first 5 rows
                print(f"      Columns: {list(df.columns)}")
                print(f"      Sample rows: {len(df)}")
            except Exception as e:
                print(f"      ❌ Error reading: {e}")
    else:
        print("  ❌ existing_tables directory not found")
    
    print("✅ Anchor file analysis completed\n")


def main():
    """Run all table creation tests."""
    print("🚀 Starting Table Creation Tests\n")
    
    try:
        test_create_from_anchor()
        test_anchor_file_analysis()
        
        print("🎉 All table creation tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    from pathlib import Path
    import pandas as pd
    exit(main())
