# Amazon Monthly Rankings Pivot Table System

A powerful, multi-dimensional analytics platform that transforms monthly Brand Analytics CSV files into comprehensive pivot tables with dynamic category expansion and intelligent data management.

## 🎯 What It Does

**Multi-Dimensional Pivot Tables**: Creates sophisticated analytics tables that organize data hierarchically:
- **Countries** → **Categories** → **Monthly Rankings**
- **Keywords as rows** with **category presence indicators** (0/1 flags)
- **Dynamic expansion** for unlimited categories and months
- **Smart data merging** that preserves existing data while adding new information

## 🏗️ Architecture

```
project/
├── DATA/                    # Raw input files (monthly CSVs)
├── outputs/                 # Processed pivot tables
├── src/                     # Source code
├── tests/                   # Test files
└── existing_tables/         # Anchor files for table creation
```

## 🚀 Key Features

### **Smart Data Detection**
- **Automatic country detection** from folder structure
- **Dynamic category discovery** within each country
- **Intelligent file parsing** for various CSV formats
- **Processing status tracking** without duplicating raw data

### **Multi-Dimensional Tables**
- **Category columns**: 0/1 indicators for keyword presence
- **Monthly columns**: Actual ranking data (Search Frequency Rank)
- **Keyword preservation**: Maintains latest month's search term order
- **Data integrity**: No overwriting of existing information

### **Dynamic Expansion**
- **Add new categories** incrementally to existing tables
- **Add new months** to expand temporal coverage
- **Smart merging**: New keywords added as rows, existing ones updated
- **Column ordering**: Maintains Search Term | Categories | Months structure

### **Intelligent Update System**
- **Change analysis**: Automatically detects what's new
- **Update reports**: Comprehensive analysis of available updates
- **User control**: Interactive prompts for update decisions
- **Confirmation system**: Prevents accidental data changes

## 📊 Output Format

The final pivot table has this structure:

| Search Term | Beauty | Grocery | Health&PersonalCare | 2023-August | 2023-September | ... |
|-------------|--------|---------|---------------------|-------------|-----------------|-----|
| magnesium glycinate | 1 | 0 | 1 | 1250 | 1180 | ... |
| vitamin d3 | 1 | 1 | 1 | 890 | 920 | ... |
| protein powder | 0 | 1 | 0 | 2100 | 1950 | ... |

**Features:**
- ✅ **Category presence**: 1 if keyword exists in category, 0 otherwise
- ✅ **Monthly rankings**: Actual Search Frequency Rank values
- ✅ **Latest month order**: Preserves search term sequence from most recent month
- ✅ **Dynamic columns**: Automatically expands with new categories/months
- ✅ **Data preservation**: Never overwrites existing information

## 🛠️ How to Use

### **1. Setup Your Data Structure**
```
DATA/
├── CANADA/
│   ├── Beauty/
│   │   ├── CA_Top_search_terms_Simple_Month_2025_07_31.csv
│   │   └── ...
│   ├── Grocery/
│   └── Health&PersonalCare/
└── US/
    ├── Beauty/
    ├── Grocery/
    └── ...
```

### **2. Create Initial Pivot Tables**
```python
from src.pivot_table_manager_enhanced import PivotTableManager

# Create Canada pivot table
manager = PivotTableManager('CANADA')
table = manager.create_from_anchor('Beauty', 'existing_tables/canada_beauty_anchor.csv')

# Add more categories
manager.import_category_data('Grocery', 'DATA/CANADA/Grocery/')
manager.import_category_data('Health&PersonalCare', 'DATA/CANADA/Health&PersonalCare/')
```

### **3. Expand with New Data**
```python
# Add new months to existing categories
manager.expand_monthly_columns('Beauty')

# Analyze what's new
analysis = manager.analyze_changes()
report = manager.generate_update_report(analysis)

# Interactive update interface
decision = manager.prompt_user_for_updates(analysis)
manager.execute_user_decision(decision)
```

### **4. Smart Updates**
```python
# The system automatically:
# - Detects new monthly files
# - Identifies new categories
# - Suggests update strategies
# - Preserves all existing data
# - Maintains table structure
```

## 📈 Current Capabilities

### **Phase 1: Foundation** ✅
- Core classes for table management
- Processing status tracking
- Metadata persistence

### **Phase 2: Table Creation** ✅
- Multi-dimensional pivot table creation
- Category expansion and data import
- Smart data merging and preservation

### **Phase 3: Dynamic Expansion** ✅
- Category addition with 0/1 indicators
- Month expansion for temporal coverage
- Smart update system with change detection

### **Phase 4: User Interface** ✅
- Interactive update prompts
- User decision system
- Confirmation and error handling

### **Phase 5: Integration & Testing** 🚧
- End-to-end workflow testing
- Performance optimization
- Final documentation

## 🔧 Technical Requirements

- **Python 3.8+**
- **pandas >= 1.5.0**
- **File structure**: DATA/country/category/monthly_files.csv

## 📁 File Locations

- **Output tables**: `outputs/canada_pivot_table.csv`, `outputs/us_pivot_table.csv`
- **Metadata**: `outputs/metadata/` (JSON state files)
- **Source code**: `src/` (Python modules)
- **Test files**: `src/test_*.py`

## 🎮 Interactive Features

### **Update Decision Interface**
```
🎮 UPDATE DECISION INTERFACE
============================================================
🏠 Current Table State:
  Country: CANADA
  Categories: Beauty, Grocery, Health&PersonalCare
  Months: 24 (from 2023-August to 2025-July)
  Keywords: 25,987

🆕 New Data Available:
  📅 New Months: None
  🏷️  New Categories: None

🔧 What would you like to do?
  1. Add new months only
  2. Add new categories only
  3. Add both months and categories
  4. Skip updates for now
  5. View detailed analysis report
```

## 🚀 Future Enhancements

- **Batch processing** for multiple countries
- **Data visualization** and analytics dashboards
- **API integration** for automated updates
- **Cloud deployment** for team collaboration
- **Advanced filtering** and search capabilities

## 📝 Notes

- **Data preservation**: Raw input files can be deleted after processing
- **Single source of truth**: Pivot tables become the authoritative data source
- **Scalable architecture**: Handles unlimited categories and months
- **Memory efficient**: Processes large datasets without memory issues
- **Error recovery**: Graceful handling of file issues and user mistakes

## 🤝 Contributing

This system is designed for Amazon R&D team use. The modular architecture makes it easy to:
- Add new data sources
- Implement new analysis features
- Extend category detection
- Optimize performance for specific use cases
