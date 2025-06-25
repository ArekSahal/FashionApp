# Color Extraction for Fashion App

This document explains the color extraction functionality that has been added to the Fashion App, allowing you to extract color information from clothing images including tone, hue, and shade analysis.

## Overview

The color extraction system uses **Pylette** to extract color palettes from product images and analyzes them using HSL/HSV color spaces to determine:

- **Tone**: Lightness-based classification (very_dark, dark, medium, light, very_light)
- **Hue**: Color category (red, orange, yellow, green, cyan, blue, magenta, pink)
- **Shade**: Saturation-based classification (muted, soft, vibrant, intense)

## New Files Added

### 1. `color_extractor.py`
Main color extraction module with the following key classes and functions:

- **`ColorExtractor`**: Main class for extracting and analyzing colors
- **`extract_colors_from_product_image()`**: Convenience function for product images
- **`get_dominant_colors_summary()`**: Generate color analysis summaries
- **`create_color_visualization()`**: Create comprehensive color visualizations

### 2. `test_color_extraction.py`
Test script that demonstrates color extraction functionality:
- Fetches a single product from Zalando
- Extracts colors from the product image
- Creates multiple visualizations
- Displays detailed color analysis

## Dependencies Required

Add these to your `requirements.txt`:

```
pylette>=1.0.0
Pillow>=10.0.0
matplotlib>=3.7.0
numpy>=1.24.0
```

Install with:
```bash
pip install pylette Pillow matplotlib numpy
```

## Updated Files

### 1. `detailed_product_collector.py`
Enhanced to include color extraction:
- Imports `extract_colors_from_product_image`
- Extracts colors for each product during data collection
- Adds color information to product data

### 2. `zalando_scraper.py`
Updated table and CSV functions to include color columns:
- **`create_product_table()`**: Now includes color columns in display
- **`save_products_to_csv()`**: Includes all color fields in CSV output

## New Color Fields Added

Each product now includes these color-related fields:

| Field | Description |
|-------|-------------|
| `dominant_color_hex` | Hex code of dominant color |
| `dominant_color_rgb` | RGB values of dominant color |
| `dominant_tone` | Tone classification of dominant color |
| `dominant_hue` | Hue category of dominant color |
| `dominant_shade` | Shade classification of dominant color |
| `overall_tone` | Most common tone across all colors |
| `overall_hue` | Most common hue across all colors |
| `overall_shade` | Most common shade across all colors |
| `color_count` | Number of colors extracted |
| `neutral_colors` | Number of neutral colors found |
| `color_extraction_success` | Whether color extraction succeeded |

## Usage Examples

### 1. Basic Color Extraction

```python
from color_extractor import extract_colors_from_product_image

# Extract colors from a product image
color_data = extract_colors_from_product_image("https://example.com/image.jpg")

if color_data['success']:
    print(f"Dominant color: {color_data['summary']['dominant_color']['hex']}")
    print(f"Dominant tone: {color_data['summary']['dominant_color']['tone']}")
    print(f"Dominant hue: {color_data['summary']['dominant_color']['hue']}")
```

### 2. Advanced Color Analysis

```python
from color_extractor import ColorExtractor

extractor = ColorExtractor(palette_size=8)
colors_data = extractor.extract_colors_from_url("https://example.com/image.jpg")

# Get detailed analysis
summary = extractor.get_dominant_colors_summary(colors_data)
print(f"Overall tone: {summary['overall_tone']}")
print(f"Color breakdown: {summary['color_breakdown']}")
```

### 3. Create Visualizations

```python
# Create comprehensive visualization
extractor.create_color_visualization(
    colors_data, 
    image_url="https://example.com/image.jpg",
    save_path="color_analysis.png"
)
```

### 4. Run Detailed Product Collection with Colors

```python
from detailed_product_collector import get_specific_clothing_types_detailed_data

# Collect products with color analysis
products = get_specific_clothing_types_detailed_data(['shirts', 't_shirts'], items_per_type=3)

# Each product now includes color information
for product in products:
    print(f"Product: {product['name']}")
    print(f"Dominant color: {product['dominant_color_hex']}")
    print(f"Tone: {product['dominant_tone']}")
    print(f"Hue: {product['dominant_hue']}")
    print(f"Shade: {product['dominant_shade']}")
```

### 5. Test Color Extraction

```bash
python test_color_extraction.py
```

This will:
- Fetch a single t-shirt product
- Extract colors from the image
- Create multiple visualizations
- Save results to `color_analysis_output/` directory

## Color Analysis Features

### Tone Classification
- **very_dark**: Lightness < 20%
- **dark**: Lightness 20-40%
- **medium**: Lightness 40-60%
- **light**: Lightness 60-80%
- **very_light**: Lightness > 80%

### Hue Categories
- **red**: 0-15° or 345-360°
- **orange**: 15-45°
- **yellow**: 45-75°
- **green**: 75-165°
- **cyan**: 165-195°
- **blue**: 195-255°
- **magenta**: 255-285°
- **pink**: 285-345°

### Shade Classification
- **muted**: Saturation < 20%
- **soft**: Saturation 20-50%
- **vibrant**: Saturation 50-80%
- **intense**: Saturation > 80%

## Visualization Outputs

The test script creates several visualizations:

1. **Main Analysis**: 4-panel comprehensive view
2. **Detailed Palette**: Color palette with analysis
3. **HSL Analysis**: HSL color space scatter plots
4. **Characteristics Breakdown**: Pie charts of tones, hues, shades
5. **Summary**: Text-based summary statistics

## Enhanced Statistics

The detailed product collector now includes color analysis statistics:

- Successful color extraction rate
- Distribution of dominant tones
- Distribution of dominant hues
- Distribution of dominant shades
- Average colors per product
- Products with neutral colors

## Error Handling

The color extraction system includes robust error handling:

- Failed image downloads
- Invalid image formats
- Network timeouts
- Color extraction failures

All errors are logged and the system continues processing other products.

## Performance Considerations

- Color extraction adds processing time per product
- Images are resized for faster processing
- Palette size can be adjusted (default: 5 colors)
- Headless browser mode recommended for batch processing

## Future Enhancements

Potential improvements:
- Color harmony analysis
- Seasonal color classification
- Brand color matching
- Color trend analysis
- Batch processing optimization 