# Supabase Integration Setup Guide

This guide explains how to set up and use the Supabase database integration for the Fashion App product collector.

## Overview

The Fashion App now supports storing product data in a Supabase database instead of CSV files. This provides:

- **Persistent storage** - Data is stored in the cloud
- **Duplicate prevention** - Automatically skips products that have already been scraped
- **Real-time access** - Data can be accessed from anywhere
- **Scalability** - No local file size limitations

## Prerequisites

1. A Supabase account (free tier available)
2. Python 3.8+ with pip
3. The Fashion App dependencies installed

## Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Create a new project
4. Note your project URL (e.g., `https://ohgyxtkvyffvycfpvxcq.supabase.co`)

## Step 2: Create the Database Table

1. In your Supabase dashboard, go to **SQL Editor**
2. Run the following SQL to create the `clothes_db` table:

```sql
CREATE TABLE public.clothes_db (
    id BIGSERIAL PRIMARY KEY,
    clothing_type TEXT,
    name TEXT,
    price TEXT,
    material TEXT,
    description TEXT,
    article_number TEXT,
    manufacturing_info TEXT,
    original_url TEXT UNIQUE,
    image_url TEXT,
    original_image_url TEXT,
    packshot_found BOOLEAN DEFAULT FALSE,
    dominant_color_hex TEXT,
    dominant_color_rgb TEXT,
    dominant_tone TEXT,
    dominant_hue TEXT,
    dominant_shade TEXT,
    overall_tone TEXT,
    overall_hue TEXT,
    overall_shade TEXT,
    color_count INTEGER DEFAULT 0,
    neutral_colors INTEGER DEFAULT 0,
    color_extraction_success BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Step 3: Get Your API Key

1. In your Supabase dashboard, go to **Settings** > **API**
2. Copy the **anon public** key (not the service_role key)
3. This key will look something like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## Step 4: Set Environment Variables

### Option A: Temporary (for current session)
```bash
export SUPABASE_KEY='your-anon-public-key-here'
```

### Option B: Permanent (recommended)
Add to your shell profile file:

**For bash:**
```bash
echo 'export SUPABASE_KEY="your-anon-public-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**For zsh:**
```bash
echo 'export SUPABASE_KEY="your-anon-public-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 6: Test the Connection

Run the test script to verify everything is working:

```bash
python test_supabase_connection.py
```

You should see output like:
```
============================================================
SUPABASE CONNECTION TEST
============================================================
✅ SUPABASE_KEY environment variable is set
Key starts with: eyJhbGciOi...

🔌 Testing database connection...
✅ Database connection successful!

📊 Database Statistics:
   Total products: 0
   Database URL: https://ohgyxtkvyffvycfpvxcq.supabase.co

🔍 Testing existing URL retrieval...
   Found 0 existing product URLs

🎉 Everything is set up correctly!
You can now run the detailed product collector:
python detailed_product_collector.py
```

## Step 7: Run the Product Collector

Now you can run the enhanced product collector:

```bash
python detailed_product_collector.py
```

The script will now:
1. Ask you to choose between Supabase Database or CSV storage
2. Check for existing products in the database
3. Skip any products that have already been scraped
4. Save new products to the database
5. Show real-time progress and statistics

## Features

### Duplicate Prevention
The script automatically downloads a list of existing product URLs from your database and skips any products that have already been processed. This prevents:
- Wasting time re-scraping the same products
- Duplicate entries in your database
- Unnecessary API calls

### Real-time Statistics
The script provides detailed statistics about:
- Total products processed
- Products skipped (duplicates)
- Database connection status
- Products by clothing type

### Fallback Mode
If the database connection fails, the script automatically falls back to CSV mode, ensuring your data collection continues uninterrupted.

## Database Schema

The `clothes_db` table includes all the product information:

| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Primary key |
| clothing_type | TEXT | Type of clothing (shirts, t_shirts, etc.) |
| name | TEXT | Product name |
| price | TEXT | Product price |
| material | TEXT | Material information |
| description | TEXT | Product description |
| article_number | TEXT | Article/part number |
| manufacturing_info | TEXT | Manufacturing details |
| original_url | TEXT | Original Zalando URL (unique) |
| image_url | TEXT | Final image URL (packshot if available) |
| original_image_url | TEXT | Original image URL |
| packshot_found | BOOLEAN | Whether packshot image was found |
| dominant_color_hex | TEXT | Dominant color in hex |
| dominant_color_rgb | TEXT | Dominant color in RGB |
| dominant_tone | TEXT | Dominant color tone |
| dominant_hue | TEXT | Dominant color hue |
| dominant_shade | TEXT | Dominant color shade |
| overall_tone | TEXT | Overall color tone |
| overall_hue | TEXT | Overall color hue |
| overall_shade | TEXT | Overall color shade |
| color_count | INTEGER | Number of colors detected |
| neutral_colors | INTEGER | Number of neutral colors |
| color_extraction_success | BOOLEAN | Whether color extraction succeeded |
| created_at | TIMESTAMP | When the record was created |

## Troubleshooting

### "SUPABASE_KEY environment variable is not set"
- Make sure you've set the environment variable correctly
- Try running `echo $SUPABASE_KEY` to verify it's set
- Restart your terminal after setting the variable

### "Database connection failed"
- Check if your Supabase project URL is correct
- Verify your API key is the "anon public" key, not the service_role key
- Make sure your IP address is allowed in Supabase settings
- Check if the `clothes_db` table exists

### "Table does not exist"
- Run the SQL create table command in your Supabase SQL Editor
- Make sure you're using the correct schema (public)

### "Permission denied"
- Check your Supabase Row Level Security (RLS) settings
- Make sure the `clothes_db` table allows insert operations for anonymous users

## Security Notes

- The script uses the "anon public" key, which is safe to use in client applications
- The `original_url` field has a UNIQUE constraint to prevent duplicates
- All data is stored in the public schema
- Consider setting up Row Level Security (RLS) policies for production use

## Next Steps

Once your data is in Supabase, you can:
1. Query it directly from the Supabase dashboard
2. Use the Supabase client in other applications
3. Set up real-time subscriptions
4. Create APIs to access the data
5. Build web applications that use the product data

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Run `python test_supabase_connection.py` for diagnostics
3. Check your Supabase project logs
4. Verify your environment variables are set correctly 