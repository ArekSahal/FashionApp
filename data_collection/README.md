# Data Collection Module

This module handles all data collection, scraping, and database operations for the FashionApp.

## Purpose
- Scrape product data from Zalando
- Extract color information from product images
- Upload product data to Supabase database
- Manage bulk data collection operations

## Files

### Core Scraping & Data Collection
- **`zalando_scraper.py`** - Main scraping functionality for Zalando products
- **`color_extractor.py`** - Color analysis and extraction from product images
- **`supabase_db.py`** - Database operations and Supabase integration

### Collection Scripts
- **`bulk_product_collector.py`** - Automated bulk collection of products (100 items per type)
- **`detailed_product_collector.py`** - Detailed product collection with individual processing
- **`zalando_exctractor/`** - Additional extraction utilities

## Usage

### Bulk Collection (Recommended)
```bash
cd data_collection
python bulk_product_collector.py
```

### Detailed Collection
```bash
cd data_collection
python detailed_product_collector.py
```

### Individual Components
```python
from zalando_scraper import get_zalando_products
from color_extractor import extract_colors_from_product_image
from supabase_db import SupabaseDB

# Scrape products
products = get_zalando_products('shirts', {'color': 'BLUE'})

# Extract colors
color_data = extract_colors_from_product_image(image_url)

# Save to database
db = SupabaseDB()
db.insert_product(product_data)
```

## Configuration
- Database credentials are managed in `../keys.py`
- All scraping parameters are configurable in the individual scripts
- Batch sizes and collection limits can be adjusted as needed

## Dependencies
- Selenium WebDriver (Firefox)
- OpenCV for image processing
- Supabase Python client
- tqdm for progress tracking 