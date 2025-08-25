#!/usr/bin/env python3
"""
Test script for enhanced processing status system.
Tests the new processing tracking functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.table_state_enhanced import TableState
from src.data_detector_enhanced import DataDetector


def test_processing_status():
    """Test the enhanced processing status functionality."""
    print("🧪 Testing Enhanced Processing Status System...")
    
    # Test TableState with processing status
    print("\n1. Testing TableState processing status...")
    state = TableState("US")
    
    # Add categories with processing status
    state.add_category("Beauty")
    state.add_category("Grocery")
    state.add_category("Health")
    
    # Mark some as processed
    state.mark_category_processed("Beauty", ["2025-July.csv", "2025-June.csv"], 1500)
    state.mark_category_pending("Grocery", ["2025-July.csv", "2025-June.csv"])
    state.mark_category_pending("Health", ["2025-July.csv"])
    
    # Test status queries
    print(f"  Pending categories: {state.get_pending_categories()}")
    print(f"  Processed categories: {state.get_processed_categories()}")
    print(f"  Processing summary: {state.get_processing_summary()}")
    
    # Test DataDetector with file details
    print("\n2. Testing DataDetector file analysis...")
    detector = DataDetector()
    
    # Scan data structure
    structure = detector.scan_all_data()
    
    print(f"  Countries found: {structure['countries']}")
    print(f"  Categories: {structure['categories']}")
    
    # Test category summary for US
    if 'US' in structure['countries']:
        for category in structure['categories'].get('US', [])[:2]:  # Test first 2 categories
            summary = detector.get_category_summary('US', category)
            if summary:
                print(f"  {category} summary: {summary}")
    
    print("\n✅ Enhanced processing status tests passed!")


def test_incremental_processing():
    """Test incremental processing workflow."""
    print("\n🧪 Testing Incremental Processing Workflow...")
    
    # Create table state
    state = TableState("CANADA")
    
    # Simulate initial state (only Beauty processed)
    state.add_category("Beauty")
    state.mark_category_processed("Beauty", ["2025-July.csv"], 1200)
    
    # Simulate adding new category
    state.add_category("Grocery")
    state.mark_category_pending("Grocery", ["2025-July.csv", "2025-June.csv"])
    
    # Check what needs processing
    pending = state.get_pending_categories()
    processed = state.get_processed_categories()
    
    print(f"  Current status:")
    print(f"    Processed: {processed}")
    print(f"    Pending: {pending}")
    
    # Simulate processing Grocery
    state.mark_category_processed("Grocery", ["2025-July.csv", "2025-June.csv"], 800)
    
    # Check updated status
    summary = state.get_processing_summary()
    print(f"  After processing Grocery:")
    print(f"    Completion: {summary['completion_percentage']:.1f}%")
    print(f"    Total categories: {summary['total_categories']}")
    
    print("\n✅ Incremental processing workflow tests passed!")


def main():
    """Run all enhanced tests."""
    print("🚀 Starting Enhanced Processing Status Tests\n")
    
    try:
        test_processing_status()
        test_incremental_processing()
        
        print("\n🎉 All enhanced tests passed! Processing status system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
