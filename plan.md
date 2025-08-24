# 🚀 Refactoring Plan: Monthly Rankings to Multi-Dimensional Pivot

## 📋 Overview
Transform the current monthly rankings merger into a hierarchical pivot table system that handles countries → categories → monthly data with dynamic expansion capabilities.

## 🎯 Target Architecture
```
Input: DATA/country/category/monthly_files.csv
Output: pivot_table.csv with columns:
kw | Beauty | Health | Grocery | 2023-Aug | 2023-Sep | 2024-Jan | ...
```

---

## 📝 Phase 1: Foundation & Structure Setup

### 1.1 Environment Setup
- [ ] **Create new project structure**
  - [ ] Create `src/` folder for source code
  - [ ] Create `tests/` folder for test files
  - [ ] Create `data/` folder for processed data
  - [ ] Move existing script to `src/`

- [ ] **Update .gitignore**
  - [ ] Exclude `data/` folder (processed outputs)
  - [ ] Keep `DATA/` folder (raw inputs)
  - [ ] Add test coverage files

### 1.2 Core Classes Design
- [ ] **Create `PivotTableManager` class**
  - [ ] Initialize with existing table or create new
  - [ ] Track current structure (categories, months, keywords)
  - [ ] Methods: `get_structure()`, `get_categories()`, `get_months()`

- [ ] **Create `DataDetector` class**
  - [ ] Scan `DATA/` folder for countries
  - [ ] Detect categories within each country
  - [ ] Parse monthly file naming conventions
  - [ ] Methods: `detect_countries()`, `detect_categories()`, `detect_months()`

- [ ] **Create `TableState` class**
  - [ ] Store current table metadata
  - [ ] Track column types (category vs month)
  - [ ] Methods: `add_category()`, `add_month()`, `get_schema()`

---

## 🔧 Phase 2: Core Functionality Implementation

### 2.1 Table Creation & Management
- [ ] **Implement base table creation**
  - [ ] Start with one category as anchor
  - [ ] Create category presence column (0/1)
  - [ ] Import all monthly data from anchor category
  - [ ] Set search terms as index, preserve order

- [ ] **Implement table state persistence**
  - [ ] Save table structure to JSON metadata
  - [ ] Save current table state
  - [ ] Methods: `save_state()`, `load_state()`, `get_diff()`

### 2.2 Data Import & Processing
- [ ] **Implement category data import**
  - [ ] Parse CSV files with proper headers
  - [ ] Extract search terms and rankings
  - [ ] Handle missing data (fill with 0s)
  - [ ] Methods: `import_category()`, `process_monthly_data()`

- [ ] **Implement data merging logic**
  - [ ] Merge new keywords (add rows)
  - [ ] Update existing keywords (preserve data)
  - [ ] Handle category presence updates
  - [ ] Methods: `merge_category()`, `add_keywords()`, `update_presence()`

---

## �� Phase 3: Dynamic Expansion System

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
  - [ ] `PivotTableManager` tests
  - [ ] `DataDetector` tests
  - [ ] `TableState` tests
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

## �� Phase 6: Migration & Cleanup

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
1. Review and approve this plan
2. Start with Phase 1.1 (Environment Setup)
3. Create basic class structure
4. Implement core functionality incrementally
5. Test each phase before moving to the next

---

*Last Updated: August 24, 2025*
*Status: Planning Phase*
