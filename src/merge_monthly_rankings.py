import pandas as pd
import os
import glob
from datetime import datetime

def extract_month_info(filename):
    """Extract year and month from filename, handling both naming formats"""
    filename = os.path.basename(filename)
    
    # Handle new format: US_Top_search_terms_Simple_Month_2025_06_30.csv
    if filename.startswith("US_Top_search_terms_Simple_Month_"):
        try:
            # Extract date part: 2025_06_30
            date_part = filename.replace("US_Top_search_terms_Simple_Month_", "").replace(".csv", "")
            year, month, day = date_part.split("_")
            
            # Convert month number to month name
            month_names = ["January", "February", "March", "April", "May", "June", 
                          "July", "August", "September", "October", "November", "December"]
            month_name = month_names[int(month) - 1]
            
            return f"{year}-{month_name}"
        except:
            return None
    
    # Handle old format: 2025-July.csv
    elif "-" in filename and filename.replace(".csv", "").split("-")[0].isdigit():
        try:
            year_month = filename.replace(".csv", "")
            return year_month
        except:
            return None
    
    return None

def merge_monthly_rankings():
    # Automatically detect CSV files in the csv folder
    csv_files = glob.glob("csv/*.csv")
    
    if not csv_files:
        print("No CSV files found in csv/ folder!")
        return
    
    # Create files dictionary automatically
    files = {}
    for csv_file in csv_files:
        year_month = extract_month_info(csv_file)
        if year_month:
            files[year_month] = csv_file
        else:
            print(f"Warning: Could not parse month info from {csv_file}")
    
    if not files:
        print("No valid CSV files found!")
        return
    
    print("Starting to merge monthly sheets (final version)...")
    print(f"Found {len(files)} CSV files: {list(files.keys())}")
    
    dfs = []
    for year_month, file in files.items():
        print(f"\nProcessing {year_month} from {file}...")
        
        try:
            # Read CSV starting from row 2 (skip metadata row, use row 1 as headers)
            # Only read Search Term and Rank columns
            columns_to_read = ["Search Term", "Search Frequency Rank"]
            print(f"Reading columns: {columns_to_read}")
            
            df = pd.read_csv(file, skiprows=1, usecols=columns_to_read)
            
            print(f"Loaded {len(df)} rows for {year_month}")
            
            # Rename the rank column to the year-month
            df = df.rename(columns={"Search Frequency Rank": year_month})
            
            # Remove any duplicates but DON'T sort - preserve original order
            df = df.drop_duplicates(subset=["Search Term"])
            
            print(f"After deduplication: {len(df)} unique search terms for {year_month}")
            
            dfs.append(df)
            
        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue
    
    if not dfs:
        print("No data loaded. Exiting.")
        return
    
    print(f"\nFiltering keywords with rankings > 500,000...")
    
    # Filter out keywords with rankings > 500,000 in each month
    filtered_dfs = []
    for df in dfs:
        year_month_name = None
        for col in df.columns:
            if col != "Search Term":
                year_month_name = col
                break
        
        if year_month_name:
            # Filter out rankings > 500,000
            original_count = len(df)
            df_filtered = df[df[year_month_name] <= 500000].copy()
            filtered_count = len(df_filtered)
            
            print(f"{year_month_name}: {original_count} -> {filtered_count} keywords (removed {original_count - filtered_count} with rank > 500,000)")
            filtered_dfs.append(df_filtered)
    
    print(f"\nMerging {len(filtered_dfs)} dataframes...")
    
    # Automatically find the latest month and year to use as the base
    print("Finding the latest month and year to use as base...")
    
    # Create a list of all available year-month combinations with their chronological order
    available_months = []
    for year_month in files.keys():
        if '-' in year_month:
            year, month = year_month.split('-')
            month_order = ["January", "February", "March", "April", "May", "June", 
                          "July", "August", "September", "October", "November", "December"]
            try:
                month_num = month_order.index(month)
                available_months.append((year_month, int(year), month_num))
            except ValueError:
                continue
    
    if available_months:
        # Sort by year first, then by month number to find the latest
        available_months.sort(key=lambda x: (x[1], x[2]), reverse=True)
        latest_year_month = available_months[0][0]
        print(f"Latest month found: {latest_year_month}")
    else:
        # Fallback: use the last file as base
        latest_year_month = list(files.keys())[-1]
        print(f"Could not parse month info, using {latest_year_month} as base")
    
    # Find the dataframe corresponding to the latest month
    base_df = None
    base_month = latest_year_month
    for df in filtered_dfs:
        if latest_year_month in df.columns:
            base_df = df
            break
    
    if base_df is None:
        # If the latest month dataframe is not found, use the last available one
        base_df = filtered_dfs[-1]
        base_month = [col for col in base_df.columns if col != "Search Term"][0]
        print(f"Latest month dataframe not found, using {base_month} as base")
    else:
        print(f"Using {base_month} as the base month (latest available)")
    
    # Start with base month's search terms in their ORIGINAL order (no sorting!)
    final_df = base_df[["Search Term"]].copy()
    print(f"Using {len(final_df)} search terms from {base_month} in ORIGINAL order")
    
    # Add base month rankings
    final_df = pd.merge(final_df, base_df[["Search Term", base_month]], on="Search Term", how="left")
    
    # Add other months' rankings
    for df in filtered_dfs:
        year_month_name = None
        for col in df.columns:
            if col != "Search Term":
                year_month_name = col
                break
        
        if year_month_name and year_month_name != base_month:
            print(f"Adding {year_month_name} rankings...")
            final_df = pd.merge(final_df, df[["Search Term", year_month_name]], on="Search Term", how="left")
    
    # Reorder columns: Search Term first, then months in chronological order
    search_term_col = "Search Term"
    rank_cols = [col for col in final_df.columns if col != search_term_col]
    
    # Sort rank columns by year-month order (2023-Aug, 2023-Sep, ..., 2025-Jul)
    def sort_key(x):
        if '-' in x:
            year, month = x.split('-')
            month_order = ["January", "February", "March", "April", "May", "June", 
                          "July", "August", "September", "October", "November", "December"]
            return (int(year), month_order.index(month))
        return (9999, 999)
    
    rank_cols = sorted(rank_cols, key=sort_key)
    
    final_columns = [search_term_col] + rank_cols
    final_df = final_df[final_columns]
    
    # Fill empty/NaN values with 0s
    print("Filling empty values with 0s...")
    final_df[rank_cols] = final_df[rank_cols].fillna(0)
    
    # Convert ranking columns to integers (remove decimal places)
    print("Converting rankings to integers...")
    for col in rank_cols:
        final_df[col] = pd.to_numeric(final_df[col], errors='coerce').astype('Int64')  # Int64 handles NaN values
    
    # Save the combined table
    output_file = "monthly_rankings_combined.csv"
    final_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Successfully created {output_file}")
    print(f"Combined {len(filtered_dfs)} months into one table with {len(final_df)} unique search terms")
    print(f"Columns: {list(final_df.columns)}")
    print(f"File size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
    
    # Show sample of the data
    print(f"\nSample of merged data:")
    print(final_df.head(10))
    
    # Show some statistics
    print(f"\n📊 Statistics:")
    print(f"Total unique search terms: {len(final_df)}")
    print(f"Search terms with data in both months: {len(final_df.dropna(subset=rank_cols))}")
    
    return final_df

if __name__ == "__main__":
    result = merge_monthly_rankings()
