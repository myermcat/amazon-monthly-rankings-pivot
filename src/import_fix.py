#!/usr/bin/env python3
"""
Fix the import function to handle the correct CSV structure.
"""

import pandas as pd

def test_csv_structure():
    """Test reading the CSV structure correctly."""
    file_path = "../DATA/CANADA/CANADA-Grocery/CA_Top_search_terms_Simple_Month_2025_07_31.csv"
    
    print(f"📁 Testing CSV structure: {file_path}")
    
    # Read with skiprows=1 to skip metadata row
    df = pd.read_csv(file_path, skiprows=1)
    
    print(f"📊 DataFrame shape: {df.shape}")
    print(f"��️ Columns: {list(df.columns)}")
    print(f"🔍 First few rows:")
    print(df.head(3))
    
    # Check if we have the right columns
    if 'Search Term' in df.columns and 'Search Frequency Rank' in df.columns:
        print("✅ Found required columns!")
        print(f"🔑 Sample search terms: {df['Search Term'].head(3).tolist()}")
        print(f"📈 Sample rankings: {df['Search Frequency Rank'].head(3).tolist()}")
    else:
        print("❌ Missing required columns")

if __name__ == "__main__":
    test_csv_structure()
