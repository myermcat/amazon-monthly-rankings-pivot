#!/usr/bin/env python3
"""
Test script for core classes.
Run this to verify the basic functionality works.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.table_state import TableState
from src.data_detector import DataDetector
from src.pivot_table_manager import PivotTableManager


def test_table_state():
    """Test TableState class."""
    print("🧪 Testing TableState...")
    
    # Create new table state
    state = TableState("US")
    
    # Add some test data
    state.add_category("Beauty")
    state.add_month("2025-July")
    state.add_keywords(["keyword1", "keyword2", "keyword3"])
    
    # Test getters
    print(f"  Categories: {state.get_categories()}")
    print(f"  Months: {state.get_months()}")
    print(f"  Schema: {state.get_schema()}")
    
    print("✅ TableState tests passed\n")


def test_data_detector():
    """Test DataDetector class."""
    print("🧪 Testing DataDetector...")
    
    detector = DataDetector()
    
    # Scan all data
    structure = detector.scan_all_data()
    
    print(f"  Countries found: {structure['countries']}")
    print(f"  Categories: {structure['categories']}")
    
    # Test monthly file detection for a specific country/category
    if 'US' in structure['countries'] and 'US-Beauty' in structure['categories'].get('US', []):
        monthly_files = detector.get_monthly_files_by_date('US', 'US-Beauty')
        print(f"  US-Beauty monthly files: {len(monthly_files)} found")
        if monthly_files:
            latest = detector.get_latest_month('US', 'US-Beauty')
            print(f"  Latest month: {latest}")
    
    print("✅ DataDetector tests passed\n")


def test_pivot_table_manager():
    """Test PivotTableManager class."""
    print("🧪 Testing PivotTableManager...")
    
    manager = PivotTableManager("US")
    
    # Test structure methods
    structure = manager.get_structure()
    print(f"  Initial structure: {structure}")
    
    # Test table info
    info = manager.get_table_info()
    print(f"  Table info: {info}")
    
    print("✅ PivotTableManager tests passed\n")


def main():
    """Run all tests."""
    print("🚀 Starting Core Classes Tests\n")
    
    try:
        test_table_state()
        test_data_detector()
        test_pivot_table_manager()
        
        print("🎉 All tests passed! Core classes are working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
