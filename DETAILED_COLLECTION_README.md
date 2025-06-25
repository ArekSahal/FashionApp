# Detailed Product Collection for Zalando

This document describes the new functionality added to the Zalando scraper for collecting detailed product information from specific clothing types.

## Overview

The new functionality allows you to:
1. **Fetch products from specific clothing types** - Currently supports shirts, t_shirts, and shorts
2. **Extract detailed information** - Visits each product page to get material and comprehensive product descriptions
3. **Create comprehensive tables** - Generates formatted tables with all collected information
4. **Export to CSV** - Saves all data to CSV files for further analysis

## New Functions Added

### `extract_product_details_from_page(driver, product_url)`
Extracts detailed product information from individual product pages:
- **Material** - Fabric composition
- **Description** - All product specifications in one field (collar, closure, pattern, details, etc.)
- **Article Number** - Product article number
- **Manufacturing Info** - Manufacturing information if available

### `get_specific_clothing_types_detailed_data(clothing_types, items_per_type=3)`
Main function that:
- Iterates through specified clothing types (shirts, t_shirts, shorts)
- Fetches specified number of items per type
- Visits each product page to extract detailed information
- Returns comprehensive product data

### `create_product_table(products_data)`
Creates a formatted markdown table from the collected data with columns:
- Clothing Type
- Name
- Price
- Material
- Description
- Article Number
- Original URL

### `save_products_to_csv(products_data, filename)`
Saves all collected data to a CSV file with all relevant fields.

## Usage

### Method 1: Using the dedicated script
```bash
python detailed_product_collector.py
```

This interactive script will:
- Ask for the number of items to fetch per clothing type
- Confirm before proceeding
- Collect data from shirts, t_shirts, and shorts
- Display results in a table
- Save to CSV
- Show summary statistics

### Method 2: Direct function calls
```python
from detailed_product_collector import get_specific_clothing_types_detailed_data, create_product_table, save_products_to_csv

# Collect detailed data from specific clothing types (2 items per type)
clothing_types = ['shirts', 't_shirts', 'shorts']
detailed_products = get_specific_clothing_types_detailed_data(clothing_types, items_per_type=2)

# Create table
table = create_product_table(detailed_products)
print(table)

# Save to CSV
save_products_to_csv(detailed_products, 'my_products.csv')
```

## Data Structure

Each product in the returned list contains:
```python
{
    'clothing_type': 'shirts',
    'name': 'Product Name',
    'url': 'https://www.zalando.se/product-url',
    'original_url': 'https://www.zalando.se/product-url',
    'image_url': 'https://image-url.jpg',
    'price': '299 kr',
    'material': 'Bomull 100%',
    'description': 'Krage: Kentkrage | Förslutning: Knapp | Mönster: Enfärgat | Detaljer: Knappslå | Artikelnummer: IJ022D063-K11',
    'article_number': 'IJ022D063-K11',
    'manufacturing_info': 'Se tillverkningsinformation'
}
```

## Supported Clothing Types

The system currently supports these clothing types:
- **shirts** - Men's shirts
- **t_shirts** - Men's t-shirts
- **shorts** - Men's shorts

## Description Field

The `description` field consolidates all product specifications into a single searchable field:
- **Format**: "Term: Value | Term: Value | ..."
- **Examples**: 
  - "Krage: Kentkrage | Förslutning: Knapp | Mönster: Enfärgat"
  - "Material: Bomull 100% | Artikelnummer: IJ022D063-K11"
- **Benefits**: 
  - All text available for future searches
  - Flexible format accommodates different product types
  - Easy to parse and search

## Performance Considerations

- **Time**: This process can take a while as it visits each product page individually
- **Rate Limiting**: The script includes delays to be respectful to Zalando's servers
- **Memory**: For large datasets, consider processing in batches
- **Network**: Requires stable internet connection

## Error Handling

The system includes comprehensive error handling:
- Continues processing if individual products fail
- Logs errors for debugging
- Gracefully handles missing data
- Continues to next clothing type if one fails

## Output Files

### CSV File
The CSV file contains all collected data with columns:
- clothing_type
- name
- price
- material
- description
- article_number
- manufacturing_info
- original_url
- image_url

### Console Output
- Progress updates for each clothing type
- Product processing status
- Summary statistics
- Formatted table display

## Example Output

```
============================================================
Processing clothing type: shirts
============================================================
Found 3 products for shirts

Processing product 1/3: Tommy Hilfiger Regular Fit Skjorta...
✅ Completed product 1

============================================================
PRODUCT DETAILS TABLE
============================================================
| Clothing Type | Name | Price | Material | Description | Article Number | Original URL |
|---------------|------|-------|----------|-------------|----------------|--------------|
| shirts | Tommy Hilfiger Regular Fit Skjorta... | 399 kr | Bomull 100% | Krage: Kentkrage | Förslutning: Knapp | IJ022D063-K11 | [Link](https://...) |
```

## Troubleshooting

### Common Issues

1. **No products found**: Check if the clothing type exists in the supported list
2. **Missing description info**: Some products may not have detailed specifications
3. **Page load errors**: Network issues or Zalando site changes
4. **Selector errors**: If Zalando changes their HTML structure

### Debugging

- Enable verbose logging by modifying the print statements
- Check the browser console for JavaScript errors
- Verify CSS selectors are still valid
- Test with a smaller number of items first

## Future Enhancements

Potential improvements:
- Add more clothing types
- Parallel processing for faster collection
- More detailed error reporting
- Data validation and cleaning
- Integration with databases
- Real-time monitoring of collection progress 