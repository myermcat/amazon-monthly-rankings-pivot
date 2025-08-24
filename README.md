# Monthly Rankings Merger - Brand Analytics Data Consolidation

This tool merges monthly Brand Analytics CSV files into a single pivot table format, consolidating search term rankings across different months.

## What it does

- **Input**: Multiple monthly CSV files (e.g., June, July, August)
- **Output**: Single CSV with one row per search term, columns for each month's ranking
- **Structure**: Search Term | June | July | August | etc.
- **Filtering**: Automatically removes keywords with rankings > 500,000
- **Base Order**: Uses the latest month's search term order as the foundation

## Files

- **`merge_monthly_rankings.py`** - Main script that processes your CSV files
- **`monthly_rankings_combined.csv`** - Output file (2.4 MB, 74,831 unique search terms)
- **`csv/` folder** - Where you put your monthly CSV files

## How to use

### 1. Prepare your data
Place your monthly CSV files in the `csv/` folder with names like:
- `2025-June.csv`
- `2025-July.csv`
- `2025-August.csv`
- etc.

**The script automatically detects all CSV files in the folder!**

### 2. Run the script
```bash
python3 merge_monthly_rankings.py
```

## Output format

The final CSV will have this clean structure:
- **Search Term**: The keyword/search term (using July's order as base)
- **June, July, etc.**: Monthly ranking data (Search Frequency Rank)

**Features:**
- ✅ **No extra columns** - just the data you need
- ✅ **Latest month's search term order** preserved exactly (automatically detected)
- ✅ **Rankings > 500,000 automatically filtered out**
- ✅ **Clean integer rankings** (no decimal places)
- ✅ **Smart base month detection** - automatically finds the most recent month

## Current results

- **Total unique search terms**: 74,831 (filtered from 171,415)
- **Search terms in both months**: 59,418
- **File size**: 2.4 MB (58% reduction from original)
- **Highest ranking**: 498,256 (well under 500,000 limit)

## Requirements

- Python 3.x
- pandas library (`pip3 install pandas`)

## Notes

- **Automatic file detection**: Just drop CSV files in the `csv/` folder
- **Latest month's search term order**: Automatically detected and used as the base order for the final table
- **Smart filtering**: Removes low-performing keywords (>500,000 rank) automatically
- **Memory efficient**: Only reads the columns you need
- **Scalable**: Automatically handles as many months as you add

## Adding more months

Simply add new CSV files to the `csv/` folder and run the script again. It will automatically:
1. Detect all CSV files
2. Extract month names from filenames
3. Filter out rankings > 500,000
4. Merge them into the existing structure
5. Maintain the latest month's search term order as the base (automatically detected)
