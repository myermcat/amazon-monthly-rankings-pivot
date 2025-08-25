# Amazon Monthly Rankings Pivot Table System - Usage Examples

This document provides comprehensive examples of how to use the Amazon Monthly Rankings Pivot Table System for various real-world scenarios.

## 🚀 Quick Start Examples

### **Basic Table Creation**

```python
from src.pivot_table_manager_enhanced import PivotTableManager

# Create a new pivot table for Canada
manager = PivotTableManager('CANADA')

# Create table from an anchor category (e.g., Beauty)
table = manager.create_from_anchor('Beauty', 'existing_tables/canada_beauty_anchor.csv')

print(f"✅ Created table with {len(table)} keywords")
```

### **Adding New Categories**

```python
# Add Grocery category
manager.import_category_data('Grocery', 'DATA/CANADA/Grocery/')

# Add Health & Personal Care category
manager.import_category_data('Health&PersonalCare', 'DATA/CANADA/Health&PersonalCare/')

# Check current table status
info = manager.get_table_info()
print(f"Categories: {info['categories']}")
print(f"Table dimensions: {info['dimensions']}")
```

### **Expanding with New Months**

```python
# Auto-expand months for Beauty category
manager.expand_monthly_columns('Beauty')

# Check what months are available
months = manager.get_months()
print(f"Available months: {len(months)}")
```

## 📊 Real-World Scenarios

### **Scenario 1: Initial Setup for New Country**

**Situation**: You want to create a pivot table for a new country (e.g., UK) with multiple categories.

```python
from src.pivot_table_manager_enhanced import PivotTableManager
from src.data_detector_enhanced import DataDetector

# 1. Initialize for new country
manager = PivotTableManager('UK')
detector = DataDetector()

# 2. Scan available data
scan_result = detector.scan_all_data()
uk_categories = scan_result['categories'].get('UK', [])
print(f"Available categories in UK: {uk_categories}")

# 3. Create table from first category (anchor)
if uk_categories:
    anchor_category = uk_categories[0]
    anchor_file = f"existing_tables/uk_{anchor_category.lower()}_anchor.csv"
    
    table = manager.create_from_anchor(anchor_category, anchor_file)
    print(f"✅ Created UK table with {len(table)} keywords")

# 4. Add remaining categories
for category in uk_categories[1:]:
    category_path = f"DATA/UK/{category}/"
    manager.import_category_data(category, category_path)
    print(f"✅ Added {category} category")

# 5. Final status
info = manager.get_table_info()
print(f"Final UK table: {info['dimensions']}")
print(f"Categories: {info['categories']}")
print(f"Months: {len(info['months'])}")
```

### **Scenario 2: Monthly Data Updates**

**Situation**: New monthly data has arrived for existing categories. You want to add it to the table.

```python
# 1. Analyze what's new
analysis = manager.analyze_changes()
print(f"New months: {analysis['new_months']}")
print(f"New categories: {analysis['new_categories']}")

# 2. Generate update report
report = manager.generate_update_report(analysis)
print(report)

# 3. Interactive update decision
decision = manager.prompt_user_for_updates(analysis)

# 4. Execute the decision
if decision['action'] != 'none':
    success = manager.execute_user_decision(decision)
    if success:
        print("✅ Update completed successfully!")
    else:
        print("❌ Update failed")
else:
    print("✅ No updates needed - table is current")
```

### **Scenario 3: Adding New Categories to Existing Table**

**Situation**: You want to add a new category (e.g., Electronics) to an existing pivot table.

```python
# 1. Check current table status
info = manager.get_table_info()
print(f"Current categories: {info['categories']}")

# 2. Add new category
new_category = "Electronics"
category_path = f"DATA/CANADA/{new_category}/"

try:
    updated_table = manager.import_category_data(new_category, category_path)
    print(f"✅ Successfully added {new_category} category")
    
    # 3. Verify the addition
    new_info = manager.get_table_info()
    print(f"New table dimensions: {new_info['dimensions']}")
    print(f"Updated categories: {new_info['categories']}")
    
    # 4. Check category presence indicators
    if new_category in updated_table.columns:
        presence_count = updated_table[new_category].sum()
        print(f"Keywords in {new_category}: {presence_count:,}")
    
except Exception as e:
    print(f"❌ Failed to add {new_category}: {e}")
```

### **Scenario 4: Performance Optimization for Large Datasets**

**Situation**: You're working with very large datasets and need to optimize performance.

```python
from src.performance_optimizer import PerformanceOptimizer

# 1. Initialize performance optimizer
optimizer = PerformanceOptimizer()

# 2. Check current memory usage
memory_info = optimizer.get_memory_usage()
print(f"Current memory usage: {memory_info['process_memory_mb']:.2f} MB")
print(f"System memory: {memory_info['system_memory_percent']:.1f}%")

# 3. Optimize existing table
if manager.table is not None:
    optimized_table = optimizer.optimize_dataframe(manager.table, 'balanced')
    manager.table = optimized_table
    
    # 4. Get optimization recommendations
    recommendations = optimizer.get_optimization_recommendations(manager.table)
    if recommendations:
        print("💡 Optimization recommendations:")
        for rec in recommendations:
            print(f"  • {rec}")
    else:
        print("✅ Table is already optimized")

# 5. Process large files efficiently
large_file = "DATA/CANADA/Beauty/large_dataset.csv"
if Path(large_file).exists():
    print("📁 Processing large file with chunked approach...")
    start_time = optimizer.monitor_performance("Large file processing")
    
    chunked_data = optimizer.process_large_dataset(large_file)
    
    optimizer.monitor_performance("Large file processing", start_time)
    print(f"✅ Large file processed: {chunked_data.shape}")
```

### **Scenario 5: Batch Processing Multiple Countries**

**Situation**: You need to process multiple countries and want to automate the workflow.

```python
import concurrent.futures
from pathlib import Path

def process_country(country_code):
    """Process a single country."""
    try:
        print(f"🚀 Processing {country_code}...")
        
        manager = PivotTableManager(country_code)
        
        # Check if table exists
        if manager.table_path.exists():
            print(f"📂 Loading existing {country_code} table...")
            manager.load_table()
        else:
            print(f"🆕 Creating new {country_code} table...")
            # Create from first available category
            categories = list(Path(f"DATA/{country_code}").glob("*"))
            if categories:
                anchor_category = categories[0].name
                anchor_file = f"existing_tables/{country_code.lower()}_{anchor_category.lower()}_anchor.csv"
                if Path(anchor_file).exists():
                    manager.create_from_anchor(anchor_category, anchor_file)
        
        # Get final status
        info = manager.get_table_info()
        print(f"✅ {country_code} completed: {info['dimensions']}")
        return True
        
    except Exception as e:
        print(f"❌ {country_code} failed: {e}")
        return False

# Process multiple countries
countries = ['CANADA', 'US', 'UK']
results = {}

print("🌍 Starting batch processing...")

# Sequential processing (safer for large datasets)
for country in countries:
    results[country] = process_country(country)

# Or parallel processing (faster but uses more memory)
# with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
#     future_to_country = {executor.submit(process_country, country): country for country in countries}
#     for future in concurrent.futures.as_completed(future_to_country):
#         country = future_to_country[future]
#         results[country] = future.result()

# Summary
print("\n📊 Batch Processing Summary:")
for country, success in results.items():
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"  {country}: {status}")
```

## 🔧 Advanced Usage Patterns

### **Custom Data Import Functions**

```python
def custom_category_import(manager, category_name, data_source, custom_mapping=None):
    """Custom category import with data transformation."""
    
    # Load data with custom parameters
    if custom_mapping:
        df = pd.read_csv(data_source, skiprows=1, usecols=custom_mapping.keys())
        df = df.rename(columns=custom_mapping)
    else:
        df = pd.read_csv(data_source, skiprows=1)
    
    # Custom data cleaning
    df = df.dropna(subset=['Search Term'])
    df = df[df['Search Frequency Rank'] <= 500000]  # Filter high rankings
    
    # Add to manager
    # (This would require extending the manager to accept pre-processed DataFrames)
    
    return df

# Usage
custom_mapping = {
    'search_term': 'Search Term',
    'ranking': 'Search Frequency Rank'
}

data = custom_category_import(
    manager, 
    'CustomCategory', 
    'custom_data.csv', 
    custom_mapping
)
```

### **Data Export and Sharing**

```python
def export_table_sections(manager, output_dir="exports"):
    """Export different sections of the pivot table."""
    
    if manager.table is None:
        print("❌ No table loaded")
        return
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Export categories only
    category_cols = ['Search Term'] + manager.get_categories()
    categories_df = manager.table[category_cols]
    categories_df.to_csv(output_path / "categories_only.csv", index=False)
    
    # Export monthly data only
    month_cols = ['Search Term'] + manager.get_months()
    months_df = manager.table[month_cols]
    months_df.to_csv(output_path / "monthly_data_only.csv", index=False)
    
    # Export specific category
    for category in manager.get_categories():
        category_data = manager.table[manager.table[category] == 1]
        if len(category_data) > 0:
            filename = f"{category.lower()}_keywords.csv"
            category_data.to_csv(output_path / filename, index=False)
    
    print(f"✅ Exports saved to {output_path}")

# Usage
export_table_sections(manager)
```

## 📈 Monitoring and Maintenance

### **Regular Health Checks**

```python
def perform_health_check(manager):
    """Perform comprehensive health check on the pivot table."""
    
    print("🏥 Performing Health Check...")
    
    # 1. Data integrity
    info = manager.get_table_info()
    print(f"  📊 Table dimensions: {info['dimensions']}")
    print(f"  🏷️  Categories: {len(info['categories'])}")
    print(f"  📅 Months: {len(info['months'])}")
    
    # 2. Memory usage
    if manager.table is not None:
        memory_mb = manager.table.memory_usage(deep=True).sum() / 1024 / 1024
        print(f"  💾 Memory usage: {memory_mb:.2f} MB")
        
        # Check for memory optimization opportunities
        optimizer = PerformanceOptimizer()
        recommendations = optimizer.get_optimization_recommendations(manager.table)
        if recommendations:
            print("  💡 Optimization opportunities:")
            for rec in recommendations:
                print(f"    • {rec}")
    
    # 3. Processing status
    summary = manager.get_processing_summary()
    print(f"  🔄 Processing status: {len(summary.get('processed_categories', {}))} processed")
    
    # 4. Data freshness
    structure = manager.get_structure()
    last_updated = structure.get('last_updated', 'Unknown')
    print(f"  🕒 Last updated: {last_updated}")
    
    print("✅ Health check complete")

# Usage
perform_health_check(manager)
```

### **Automated Backup and Recovery**

```python
import shutil
from datetime import datetime

def backup_table(manager, backup_dir="backups"):
    """Create backup of current table and metadata."""
    
    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup table
    if manager.table_path.exists():
        backup_file = backup_path / f"table_backup_{timestamp}.csv"
        shutil.copy2(manager.table_path, backup_file)
        print(f"✅ Table backed up: {backup_file}")
    
    # Backup metadata
    if manager.metadata_dir.exists():
        metadata_backup = backup_path / f"metadata_backup_{timestamp}"
        shutil.copytree(manager.metadata_dir, metadata_backup)
        print(f"✅ Metadata backed up: {metadata_backup}")
    
    return backup_path

def restore_table(manager, backup_file):
    """Restore table from backup."""
    
    if not Path(backup_file).exists():
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    try:
        # Restore table
        shutil.copy2(backup_file, manager.table_path)
        print(f"✅ Table restored from: {backup_file}")
        
        # Reload table
        manager.load_table()
        print("✅ Table reloaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

# Usage
# backup_table(manager)
# restore_table(manager, "backups/table_backup_20250824_143022.csv")
```

## 🎯 Best Practices

### **1. Data Organization**
- Keep raw data in `DATA/country/category/` structure
- Use consistent naming conventions for files
- Maintain anchor files in `existing_tables/` for quick table recreation

### **2. Performance Optimization**
- Use chunked processing for files > 100MB
- Monitor memory usage during large operations
- Apply optimization recommendations regularly

### **3. Error Handling**
- Always check return values from operations
- Use try-catch blocks for file operations
- Validate data before processing

### **4. Regular Maintenance**
- Perform health checks weekly
- Create backups before major updates
- Monitor processing status and clean up old metadata

### **5. Scalability**
- Process countries sequentially for very large datasets
- Use performance optimizer for memory-intensive operations
- Consider database storage for tables > 1GB

## 🚨 Troubleshooting

### **Common Issues and Solutions**

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Memory Error** | "MemoryError" during large file processing | Use `process_large_dataset()` with chunking |
| **File Not Found** | "FileNotFoundError" when importing categories | Check file paths and DATA folder structure |
| **Column Mismatch** | "KeyError" when accessing columns | Verify CSV structure and column names |
| **Slow Performance** | Operations taking > 10 seconds | Run performance optimization and check memory usage |
| **Data Loss** | Missing categories or months after update | Check backup files and verify update process |

### **Debug Mode**

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed information about all operations
manager = PivotTableManager('CANADA', debug=True)
```

## 📚 Additional Resources

- **API Reference**: See source code docstrings for detailed method documentation
- **Test Files**: Run `python3 src/test_*.py` for examples and validation
- **Performance Tuning**: Use `PerformanceOptimizer` for large dataset optimization
- **Error Recovery**: Check `backups/` folder for automatic backups

---

**Need Help?** Check the test files for working examples or run the integration test suite to verify your setup.
