# Bulk Product Collector

A fully automated script that collects 100 items from all clothing types on Zalando and uploads them to Supabase in efficient batches of 20.

## 🚀 Features

- **No User Input Required**: Runs completely automatically
- **Batch Uploads**: Uploads in batches of 20 for efficiency and data safety
- **Duplicate Prevention**: Skips products that already exist in the database
- **Comprehensive Statistics**: Shows detailed progress and results
- **Error Recovery**: If a batch fails, only that batch is lost, not all data
- **All Clothing Types**: Processes all 16 available clothing types

## 📋 Prerequisites

1. **Supabase Setup**: Make sure you have set up your Supabase database
2. **Environment Variable**: Set your Supabase key:
   ```bash
   export SUPABASE_KEY='your-supabase-anon-key'
   ```
3. **Dependencies**: Install all required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. **Firefox WebDriver**: Ensure GeckoDriver is installed and in PATH

## 🧪 Testing First

Before running the full collection, test with a small sample:

```bash
python test_bulk_collector.py
```

This will:
- Collect 5 items from the first 3 clothing types
- Upload in batches of 3
- Verify everything works correctly

## 🚀 Running the Full Collection

```bash
python bulk_product_collector.py
```

This will:
- Collect 100 items from all 16 clothing types (1,600 total products)
- Upload to Supabase in batches of 20
- Show real-time progress
- Display comprehensive statistics when complete

## ⏱️ Expected Duration

- **Test run**: ~10-15 minutes
- **Full collection**: 4-8 hours (depending on network speed and product availability)

## 📊 What Gets Collected

For each product, the script collects:

### Basic Information
- Product name, URL, and price
- Clothing type and category
- Original and packshot image URLs

### Detailed Information
- Material composition
- Product description
- Article number
- Manufacturing information

### Color Analysis
- Dominant color (hex, RGB, tone, hue, shade)
- Overall color characteristics
- Color count and neutral color detection
- Color extraction success status

## 🔄 Batch Processing

The script processes products in batches of 20 for several benefits:

1. **Data Safety**: If something fails, only the current batch is lost
2. **Memory Efficiency**: Doesn't hold all products in memory at once
3. **Progress Tracking**: Shows real-time progress for each batch
4. **Error Recovery**: Can resume from where it left off

## 📈 Statistics

The script provides comprehensive statistics including:

- Total products processed, saved, and failed
- Breakdown by clothing type
- Success rates and error tracking
- Duration and performance metrics

## 🛠️ Customization

You can modify the script to change:

- **Items per type**: Change `items_per_type=100` to any number
- **Batch size**: Change `batch_size=20` to any number
- **Clothing types**: Modify `ALL_CLOTHING_TYPES` list

## 🐛 Troubleshooting

### Common Issues

1. **Supabase Key Not Set**
   ```
   ❌ SUPABASE_KEY environment variable not set!
   ```
   Solution: Set the environment variable before running

2. **WebDriver Issues**
   ```
   ❌ Failed to initialize webdriver
   ```
   Solution: Install Firefox and GeckoDriver

3. **Network Errors**
   ```
   ❌ Error processing product
   ```
   Solution: Check internet connection and try again

4. **Memory Issues**
   ```
   ❌ Out of memory
   ```
   Solution: Reduce batch size or items per type

### Error Recovery

If the script fails partway through:
1. The script automatically skips existing products
2. You can restart it and it will continue from where it left off
3. No duplicate data will be created

## 📁 Output

The script saves all data to your Supabase database in the `products` table with the following structure:

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    clothing_type TEXT,
    name TEXT,
    url TEXT UNIQUE,
    original_url TEXT,
    image_url TEXT,
    original_image_url TEXT,
    packshot_found BOOLEAN,
    price TEXT,
    material TEXT,
    description TEXT,
    article_number TEXT,
    manufacturing_info TEXT,
    dominant_color_hex TEXT,
    dominant_color_rgb TEXT,
    dominant_tone TEXT,
    dominant_hue TEXT,
    dominant_shade TEXT,
    overall_tone TEXT,
    overall_hue TEXT,
    overall_shade TEXT,
    color_count INTEGER,
    neutral_colors INTEGER,
    color_extraction_success BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🎯 Tips for Best Results

1. **Run during off-peak hours** for better network performance
2. **Use a stable internet connection** to avoid timeouts
3. **Monitor the process** to catch any issues early
4. **Start with the test script** to verify everything works
5. **Check your Supabase dashboard** to monitor uploads

## 🔄 Resuming Interrupted Collections

If the script is interrupted:
1. Simply run it again
2. It will automatically skip existing products
3. Continue from where it left off
4. No data will be lost or duplicated

## 📞 Support

If you encounter issues:
1. Check the error messages for specific details
2. Verify your Supabase setup is correct
3. Ensure all dependencies are installed
4. Try the test script first to isolate issues 