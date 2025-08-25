#!/usr/bin/env python3
"""
Test script for month expansion functionality.
Tests adding new months to existing categories in the pivot table.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append('src')

from pivot_table_manager_enhanced import PivotTableManager
from data_detector_enhanced import DataDetector

def test_month_expansion():
    """Test month expansion functionality."""
    print("🚀 Testing Month Expansion Functionality...")
    
    # Initialize components
    country = "CANADA"
    manager = PivotTableManager(country)
    detector = DataDetector()
    
    print(f"\n📊 Current table status:")
    info = manager.get_table_info()
    print(f"  Shape: {info['dimensions']}")
    print(f"  Categories: {info['categories']}")
    print(f"  Months: {len(info['months'])}")
    
    # Test month expansion for Beauty category
    print(f"\n🔍 Testing month expansion for Beauty category...")
    
    try:
        # Auto-expand months for Beauty
        updated_table = manager.expand_monthly_columns("Beauty")
        
        if updated_table is not None:
            print(f"\n✅ Month expansion completed!")
            print(f"  New table shape: {updated_table.shape}")
            print(f"  Updated months: {manager.get_months()}")
        else:
            print("❌ Month expansion failed")
            
    except Exception as e:
        print(f"❌ Error during month expansion: {e}")
        import traceback
        traceback.print_exc()

def test_manual_month_addition():
    """Test manually adding specific month files."""
    print("\n🔧 Testing Manual Month Addition...")
    
    country = "CANADA"
    manager = PivotTableManager(country)
    detector = DataDetector()
    
    # Get available files for Beauty category
    beauty_files = detector.get_category_files(country, "Beauty")
    
    if beauty_files:
        print(f"📁 Found {len(beauty_files)} files for Beauty category")
        
        # Filter for monthly files (not combined files)
        monthly_files = [f for f in beauty_files if manager._is_monthly_file(f)]
        print(f"📅 Found {len(monthly_files)} monthly files")
        
        if monthly_files:
            # Test adding a few months
            test_files = monthly_files[:3]  # Test with first 3 files
            print(f"🧪 Testing with {len(test_files)} files: {[Path(f).name for f in test_files]}")
            
            try:
                updated_table = manager.add_new_months("Beauty", test_files)
                print(f"✅ Manual month addition completed!")
                print(f"  New table shape: {updated_table.shape}")
            except Exception as e:
                print(f"❌ Error during manual month addition: {e}")
        else:
            print("⚠️  No monthly files found for testing")
    else:
        print("⚠️  No files found for Beauty category")

if __name__ == "__main__":
    print("🧪 Month Expansion Test Suite")
    print("=" * 50)
    
    # Test 1: Auto-expansion
    test_month_expansion()
    
    # Test 2: Manual addition
    test_manual_month_addition()
    
    print("\n🎯 Test suite completed!")
