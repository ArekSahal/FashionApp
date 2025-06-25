# FashionApp Tests

This directory contains all test files for the FashionApp AI server.

## Test Files

- `test_database_search.py` - Tests for database search functionality
- `test_detailed_inventory.py` - Tests for detailed inventory system
- `test_dynamic_materials.py` - Tests for dynamic material building blocks
- `test_material_system.py` - Tests for material validation and extraction
- `test_outfit_search.py` - Tests for outfit search functionality
- `test_relevance_scoring.py` - Tests for relevance scoring system
- `test_text_search.py` - Tests for text-based search functionality
- `test_validation_system.py` - Tests for validation systems

## Example Files

- `example_detailed_inventory.py` - Example usage of detailed inventory system

## Running Tests

To run all tests:

```bash
cd tests
python -m pytest *.py
```

Or run individual test files:

```bash
python test_database_search.py
python test_outfit_search.py
```

## Test Coverage

These tests cover:
- Database connectivity and queries
- Material extraction and validation
- Outfit search algorithms
- Text search functionality
- Relevance scoring systems
- Inventory management
- API endpoints (when applicable) 