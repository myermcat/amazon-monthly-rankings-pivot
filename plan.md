# 🚀 Refactoring Plan: Monthly Rankings to Multi-Dimensional Pivot

## 📋 Overview
Transform the current monthly rankings merger into a hierarchical pivot table system that handles countries → categories → monthly data with dynamic expansion capabilities.

## 🎯 Target Architecture
```
Input: DATA/country/category/monthly_files.csv
Output: pivot_table.csv with columns:
kw | Beauty | Health | Grocery | 2023-Aug | 2023-Sep | 2024-Jan | ...
```

## 📁 Project Structure
```
project/
├── DATA/                    # Raw input files (monthly CSVs)
├── outputs/                 # Processed pivot tables
├── src/                     # Source code
├── tests/                   # Test files
└── existing_tables/         # Your current combined files as anchors
```

---

## 📝 Phase 1: Foundation & Structure Setup

### 1.1 Environment Setup
- [x] **Create new project structure**
  - [x] Create `src/` folder for source code
  - [x] Create `outputs/` folder for processed pivot tables
  - [x] Create `existing_tables/` folder for current combined files as anchors
  - [x] Create `tests/` folder for test files
  - [x] Move existing script to `src/`

- [ ] **Update .gitignore**
  - [x] Exclude `outputs/` folder (processed outputs)
  - [x] Keep `DATA/` folder (raw inputs)
  - [x] Add test coverage files

### 1.2 Core Classes Design
- [x] **Create `PivotTableManager` class**
  - [x] Initialize with existing table or create new
  - [x] Track current structure (categories, months, keywords)
  - [x] Methods: `get_structure()`, `get_categories()`, `get_months()`

- [x] **Create `DataDetector` class**
  - [x] Scan `DATA/` folder for countries
  - [x] Detect categories within each country
  - [x] Parse monthly file naming conventions
  - [x] Methods: `detect_countries()`, `detect_categories()`, `detect_months()`

- [x] **Create `TableState` class**
  - [x] Store current table metadata
  - [x] Track column types (category vs month)
  - [x] Methods: `add_category()`, `add_month()`, `get_schema()`

---

## 🔧 Phase 2: Core Functionality Implementation

### 2.1 Table Creation & Management
- [ ] **Implement base table creation**
  - [x] Start with one category as anchor (existing Beauty files)
  - [x] Create category presence column (0/1)
  - [x] Import all monthly data from anchor category
  - [x] Set search terms as index, preserve order

- [ ] **Implement table state persistence**
  - [ ] Save table structure to JSON metadata
  - [ ] Save current table state
  - [x] Methods: `save_state()`, `load_state()`, `get_diff()`

### 2.2 Data Import & Processing
- [ ] **Implement category data import**
  - [x] Parse CSV files with proper headers
  - [x] Extract search terms and rankings
  - [x] Handle missing data (fill with 0s)
  - [x] Methods: `import_category()`, `process_monthly_data()`

- [ ] **Implement data merging logic**
  - [x] Merge new keywords (add rows)
  - [x] Update existing keywords (preserve data)
  - [x] Handle category presence updates
  - [x] Methods: `merge_category()`, `add_keywords()`, `update_presence()`

---

## 🚀 Phase 3: Dynamic Expansion System

### 3.1 Category Expansion
- [ ] **Implement category addition**
  - [ ] Create new 0/1 column for new category
  - [ ] Import all monthly data from new category
  - [ ] Merge with existing table structure
  - [ ] Update category presence indicators
  - [ ] Methods: `add_new_category()`, `expand_table_columns()`

### 3.2 Month Expansion
- [ ] **Implement month addition**
  - [ ] Detect new months in existing categories
  - [ ] Add new month columns
  - [ ] Populate data from available sources
  - [ ] Fill missing data with 0s
  - [ ] Methods: `add_new_months()`, `expand_monthly_columns()`

### 3.3 Incremental Updates
- [ ] **Implement smart update system**
  - [ ] Compare new files with existing table
  - [ ] Detect what's new (months, categories, keywords)
  - [ ] Generate update report
  - [ ] Methods: `analyze_changes()`, `generate_update_report()`

---

## 🎮 Phase 4: User Interface & Control

### 4.1 Interactive Prompts
- [ ] **Implement user decision system**
  - [ ] Show what's new (months, categories, keywords)
  - [ ] Ask user what to add
  - [ ] Confirm before making changes
  - [ ] Methods: `prompt_user()`, `get_user_decision()`

### 4.2 Update Workflows
- [ ] **Implement update workflows**
  - [ ] Add missing months only
  - [ ] Add missing categories only
  - [ ] Add both months and categories
  - [ ] Methods: `update_months_only()`, `update_categories_only()`, `update_all()`

---

## 🧪 Phase 5: Testing & Validation

### 5.1 Unit Tests
- [ ] **Test core classes**
  - [x] `PivotTableManager` tests
  - [x] `DataDetector` tests
  - [x] `TableState` tests
  - [ ] Data import/merge tests

### 5.2 Integration Tests
- [ ] **Test complete workflows**
  - [ ] Create new table from scratch
  - [ ] Add new category to existing table
  - [ ] Add new months to existing table
  - [ ] Handle mixed updates

### 5.3 Data Validation Tests
- [ ] **Test data integrity**
  - [ ] No data loss during merges
  - [ ] Correct category presence indicators
  - [ ] Proper handling of missing data
  - [ ] Consistent keyword ordering

---

## 📊 Phase 6: Migration & Cleanup

### 6.1 Data Migration
- [ ] **Migrate existing data**
  - [ ] Convert current Beauty combined files to new format
  - [ ] Test with existing data structure
  - [ ] Validate output matches expectations

### 6.2 Cleanup
- [ ] **Remove old code**
  - [ ] Delete old merger script
  - [ ] Remove unused functions
  - [ ] Update documentation

---

## 🎯 Success Criteria

### Functional Requirements
- [ ] **Multi-dimensional output**: kw | Beauty | Health | Grocery | months...
- [ ] **Dynamic expansion**: Add categories and months incrementally
- [ ] **Data preservation**: No overwriting of existing data
- [ ] **User control**: Choose what to add/update
- [ ] **Future-proof**: Handle any combination of new data

### Technical Requirements
- [ ] **Modular design**: Clean separation of concerns
- [ ] **Testable code**: Comprehensive test coverage
- [ ] **Error handling**: Graceful failure and recovery
- [ ] **Performance**: Handle large datasets efficiently
- [ ] **Documentation**: Clear usage instructions

### User Experience
- [ ] **Intuitive workflow**: Easy to understand and use
- [ ] **Progress feedback**: Clear indication of what's happening
- [ ] **Decision support**: Help user make informed choices
- [ ] **Error recovery**: Easy to fix mistakes

---

## 📅 Timeline Estimate
- **Phase 1-2**: 2-3 days (Foundation & Core)
- **Phase 3**: 2-3 days (Expansion System)
- **Phase 4**: 1-2 days (User Interface)
- **Phase 5**: 2-3 days (Testing)
- **Phase 6**: 1 day (Migration)

**Total**: 8-12 days

---

## 🔍 Next Steps
1. ✅ **Environment setup complete** - Project structure created
2. **Start with Phase 1.2** (Core Classes Design)
3. **Implement table creation from anchor categories**
4. **Implement core functionality incrementally**
5. **Test each phase before moving to the next**

---

*Last Updated: August 24, 2025*
*Status: Phase 1.2 Complete - Core Classes Implemented with Processing Status*

### 1.3 Processing Status System ✅ **COMPLETED**
- [x] **Enhanced TableState** with processing status tracking
- [x] **Enhanced DataDetector** with file analysis and metadata
- [x] **Processing status persistence** in JSON metadata
- [x] **CLI status checker** for real-time monitoring
- [x] **Smart processing workflow** - track what needs attention
