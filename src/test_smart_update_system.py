#!/usr/bin/env python3
"""
Test script for the Smart Update System.
Tests change analysis and update report generation.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append('src')

from pivot_table_manager_enhanced import PivotTableManager
from data_detector_enhanced import DataDetector

def test_smart_update_system():
    """Test the smart update system functionality."""
    print("🧠 Testing Smart Update System...")
    
    # Initialize components
    country = "CANADA"
    manager = PivotTableManager(country)
    
    print(f"\n📊 Current table status:")
    info = manager.get_table_info()
    print(f"  Shape: {info['dimensions']}")
    print(f"  Categories: {info['categories']}")
    print(f"  Months: {len(info['months'])}")
    
    # Test 1: Change Analysis
    print(f"\n🔍 Testing Change Analysis...")
    try:
        analysis = manager.analyze_changes()
        
        if 'error' not in analysis:
            print(f"✅ Change analysis completed!")
            print(f"  📅 New months: {len(analysis['new_months'])}")
            print(f"  🏷️  New categories: {len(analysis['new_categories'])}")
            print(f"  🔑 New keywords: {analysis['new_keywords_count']}")
            
            if analysis['new_months']:
                print(f"    New months: {', '.join(analysis['new_months'])}")
            if analysis['new_categories']:
                print(f"    New categories: {', '.join(analysis['new_categories'])}")
        else:
            print(f"❌ Analysis failed: {analysis['error']}")
            
    except Exception as e:
        print(f"❌ Error during change analysis: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Update Report Generation
    print(f"\n📋 Testing Update Report Generation...")
    try:
        report = manager.generate_update_report()
        print(f"✅ Update report generated!")
        print(f"\n{report}")
        
    except Exception as e:
        print(f"❌ Error during report generation: {e}")
        import traceback
        traceback.print_exc()

def test_file_analysis():
    """Test file analysis with specific files."""
    print(f"\n🔍 Testing File Analysis...")
    
    country = "CANADA"
    manager = PivotTableManager(country)
    detector = DataDetector()
    
    # Get some files to analyze
    beauty_files = detector.get_category_files(country, "Beauty")
    
    if beauty_files:
        print(f"📁 Found {len(beauty_files)} files for Beauty category")
        
        # Test with a few files
        test_files = beauty_files[:3]
        print(f"🧪 Testing analysis with {len(test_files)} files")
        
        try:
            analysis = manager.analyze_changes(test_files)
            print(f"✅ File-specific analysis completed!")
            print(f"  📅 New months: {len(analysis['new_months'])}")
            print(f"  🏷️  New categories: {len(analysis['new_categories'])}")
            print(f"  🔑 New keywords: {analysis['new_keywords_count']}")
            
        except Exception as e:
            print(f"❌ Error during file analysis: {e}")
    else:
        print("⚠️  No files found for Beauty category")

if __name__ == "__main__":
    print("🧠 Smart Update System Test Suite")
    print("=" * 50)
    
    # Test 1: Smart Update System
    test_smart_update_system()
    
    # Test 2: File Analysis
    test_file_analysis()
    
    print("\n🎯 Test suite completed!")
