#!/usr/bin/env python3
"""
CLI tool for checking processing status and managing pivot tables.
Provides interactive interface for monitoring and managing data processing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.table_state_enhanced import TableState
from src.data_detector_enhanced import DataDetector


def print_status_header():
    """Print a nice header for the status display."""
    print("=" * 80)
    print("🔍 AMAZON BRAND ANALYTICS - PROCESSING STATUS CHECKER")
    print("=" * 80)


def check_country_status(country: str):
    """Check and display processing status for a specific country."""
    print(f"\n📊 Processing Status for {country.upper()}")
    print("-" * 50)
    
    # Initialize components
    state = TableState(country)
    detector = DataDetector()
    
    # Scan data structure
    structure = detector.scan_all_data()
    
    if country not in structure['countries']:
        print(f"❌ No data found for {country}")
        return
    
    # Get categories for this country
    categories = structure['categories'].get(country, [])
    
    if not categories:
        print(f"❌ No categories found for {country}")
        return
    
    # Initialize processing status for all categories
    for category in categories:
        if category not in state.processing_status:
            state.add_category(category)
            
            # Get available files for this category
            if country in detector.monthly_files and category in detector.monthly_files[country]:
                available_files = detector.monthly_files[country][category]
                state.mark_category_pending(category, available_files)
    
    # Display status
    summary = state.get_processing_summary()
    
    print(f"📈 Overall Progress: {summary['completion_percentage']:.1f}%")
    print(f"📁 Total Categories: {summary['total_categories']}")
    print(f"✅ Processed: {summary['processed']}")
    print(f"⏳ Pending: {summary['pending']}")
    
    print(f"\n📋 Category Details:")
    for category in categories:
        status = state.get_processing_status(category)
        if status.get('status') == 'processed':
            print(f"  ✅ {category}: Processed ({status.get('total_keywords', 0)} keywords)")
            if status.get('files_processed'):
                print(f"      Files: {', '.join(status['files_processed'][:3])}{'...' if len(status['files_processed']) > 3 else ''}")
        else:
            available_files = status.get('files_available', [])
            print(f"  ⏳ {category}: Pending ({len(available_files)} files available)")
            if available_files:
                print(f"      Files: {', '.join(available_files[:3])}{'...' if len(available_files) > 3 else ''}")
    
    # Show file analysis
    print(f"\n📊 File Analysis:")
    for category in categories[:3]:  # Show first 3 categories
        summary = detector.get_category_summary(country, category)
        if summary:
            print(f"  📁 {category}:")
            print(f"     Files: {summary['file_count']}, Size: {summary['total_size_mb']} MB")
            print(f"     Date Range: {summary['date_range']}")


def main():
    """Main CLI interface."""
    print_status_header()
    
    # Check status for both countries
    check_country_status("US")
    check_country_status("CANADA")
    
    print(f"\n" + "=" * 80)
    print("💡 Next Steps:")
    print("  1. Use existing Beauty files as anchors to create pivot tables")
    print("  2. Add new categories incrementally")
    print("  3. Monitor processing status in real-time")
    print("=" * 80)


if __name__ == "__main__":
    main()
