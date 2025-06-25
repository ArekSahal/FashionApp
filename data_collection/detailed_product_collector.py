#!/usr/bin/env python3
"""
Detailed Product Collector for Zalando

This script demonstrates how to collect detailed product information
from specific clothing types on Zalando, including material, collar type,
closure type, pattern, and other specifications.

This version processes products one by one and saves them to Supabase database.
"""

from zalando_scraper import (
    get_zalando_products,
    extract_product_details_from_page,
    create_product_table,
    save_products_to_csv,
    find_packshot_image,
    modify_image_url_to_packshot
)
from color_extractor import extract_colors_from_product_image
from supabase_db import SupabaseDB
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import csv
import os

def save_single_product_to_database(product_data, db_client):
    """
    Save a single product to Supabase database
    
    Args:
        product_data (dict): Product data dictionary
        db_client (SupabaseDB): Database client instance
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        success = db_client.insert_product(product_data)
        if success:
            print(f"✅ Saved product to database")
        else:
            print(f"❌ Failed to save product to database")
        return success
        
    except Exception as e:
        print(f"Error saving to database: {str(e)}")
        return False

def save_single_product_to_csv(product_data, filename, write_header=False):
    """
    Save a single product to CSV file (fallback method)
    
    Args:
        product_data (dict): Product data dictionary
        filename (str): Output CSV filename
        write_header (bool): Whether to write the header row
    """
    # Define fieldnames including color information and packshot data
    fieldnames = [
        'clothing_type', 'name', 'price', 'material', 'description', 
        'article_number', 'manufacturing_info', 'original_url', 'image_url',
        'original_image_url', 'packshot_found',
        # Color information
        'dominant_color_hex', 'dominant_color_rgb', 'dominant_tone', 
        'dominant_hue', 'dominant_shade', 'overall_tone', 'overall_hue', 
        'overall_shade', 'color_count', 'neutral_colors', 'color_extraction_success'
    ]
    
    try:
        # Check if file exists to determine if we need to write header
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header only if file is new or explicitly requested
            if write_header or not file_exists:
                writer.writeheader()
            
            # Create a clean row with only the specified fields
            row = {field: product_data.get(field, '') for field in fieldnames}
            writer.writerow(row)
        
        print(f"✅ Saved product to {filename}")
        
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")

def process_single_product(driver, product, clothing_type):
    """
    Process a single product to extract detailed information and colors
    
    Args:
        driver: Selenium WebDriver instance
        product (dict): Basic product information
        clothing_type (str): Type of clothing
    
    Returns:
        dict: Complete product information with details and colors
    """
    print(f"\nProcessing product: {product['name'][:50]}...")
    
    # Extract detailed information from product page
    print(f"  Extracting detailed information from product page...")
    detailed_info = extract_product_details_from_page(driver, product['url'])
    
    # Get packshot image for better color analysis
    print(f"  Finding packshot image for color analysis...")
    packshot_img_url = find_packshot_image(product['url'], driver)
    
    # Use packshot image if found, otherwise try to modify the original image URL
    if packshot_img_url:
        final_img_url = packshot_img_url
        packshot_found = True
        print(f"  ✅ Found packshot image: {packshot_img_url}")
    else:
        # Try to modify the original image URL to get packshot
        modified_img_url = modify_image_url_to_packshot(product['image_url'])
        if modified_img_url != product['image_url']:
            final_img_url = modified_img_url
            packshot_found = True
            print(f"  🔄 Modified image URL to packshot: {modified_img_url}")
        else:
            # Use the original image as fallback
            final_img_url = product['image_url']
            packshot_found = False
            print(f"  ⚠️ Using original image (no packshot available): {product['image_url']}")
    
    # Extract colors from the packshot image
    print(f"  Extracting colors from {'packshot' if packshot_found else 'original'} image...")
    color_data = extract_colors_from_product_image(final_img_url)
    
    # Combine basic product info with detailed info and color data
    complete_product_info = {
        'clothing_type': clothing_type,
        'name': product['name'],
        'url': product['url'],
        'original_url': product['url'],  # Keep original URL
        'image_url': final_img_url,  # Use packshot image if available
        'original_image_url': product['image_url'],  # Keep original image URL for reference
        'packshot_found': packshot_found,
        'price': product['price'],
        'material': detailed_info['material'],
        'description': detailed_info['description'],
        'article_number': detailed_info['article_number'],
        'manufacturing_info': detailed_info['manufacturing_info'],
        # Color information
        'dominant_color_hex': color_data['summary'].get('dominant_color', {}).get('hex', ''),
        'dominant_color_rgb': color_data['summary'].get('dominant_color', {}).get('rgb', ''),
        'dominant_tone': color_data['summary'].get('dominant_color', {}).get('css_color', ''),
        'dominant_hue': color_data['summary'].get('dominant_color', {}).get('css_color', ''),
        'dominant_shade': color_data['summary'].get('dominant_color', {}).get('css_color', ''),
        'overall_tone': color_data['summary'].get('overall_css_color', ''),
        'overall_hue': color_data['summary'].get('overall_css_color', ''),
        'overall_shade': color_data['summary'].get('overall_css_color', ''),
        'color_count': color_data['summary'].get('color_count', 0),
        'neutral_colors': color_data['summary'].get('neutral_colors', 0),
        'color_extraction_success': color_data['success']
    }
    
    return complete_product_info

def get_specific_clothing_types_detailed_data_individual(clothing_types, items_per_type=3, use_database=True, output_filename=None):
    """
    Fetch detailed product information from specific clothing types and save individually
    
    Args:
        clothing_types (list): List of clothing types to process
        items_per_type (int): Number of items to fetch per clothing type
        use_database (bool): Whether to save to database (True) or CSV (False)
        output_filename (str): Output CSV filename (optional, only used if use_database=False)
    
    Returns:
        int: Total number of products processed
    """
    if not use_database and output_filename is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_filename = f'zalando_detailed_products_{items_per_type}_per_type_{timestamp}.csv'
    
    total_products_processed = 0
    total_products_skipped = 0
    
    # Initialize database client if using database
    db_client = None
    existing_urls = set()
    
    if use_database:
        try:
            db_client = SupabaseDB()
            existing_urls = db_client.get_existing_product_urls()
            print(f"📊 Found {len(existing_urls)} existing products in database")
        except Exception as e:
            print(f"❌ Failed to initialize database: {str(e)}")
            print("🔄 Falling back to CSV mode")
            use_database = False
    
    # Initialize webdriver
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Firefox(options=options)
    
    try:
        # Process each specified clothing type
        for clothing_type in clothing_types:
            print(f"\n{'='*60}")
            print(f"Processing clothing type: {clothing_type}")
            print(f"{'='*60}")
            
            try:
                # Get products for this clothing type
                products = get_zalando_products(clothing_type, max_items=items_per_type)
                
                if not products:
                    print(f"No products found for {clothing_type}")
                    continue
                
                print(f"Found {len(products)} products for {clothing_type}")
                
                # Process each product individually
                for i, product in enumerate(products, 1):
                    print(f"\n--- Product {i}/{len(products)} ---")
                    
                    # Check if product URL already exists in database
                    if product['url'] in existing_urls:
                        print(f"⏭️ Skipping product (already exists in database): {product['name'][:50]}...")
                        total_products_skipped += 1
                        continue
                    
                    try:
                        # Process the product
                        complete_product_info = process_single_product(driver, product, clothing_type)
                        
                        # Save to database or CSV
                        if use_database and db_client:
                            success = save_single_product_to_database(complete_product_info, db_client)
                            if success:
                                total_products_processed += 1
                        else:
                            # Save to CSV (write header only for first product)
                            write_header = (total_products_processed == 0)
                            save_single_product_to_csv(complete_product_info, output_filename, write_header)
                            total_products_processed += 1
                        
                        print(f"✅ Completed and saved product {i}/{len(products)}")
                        
                        # Show a quick summary of what was extracted
                        print(f"   Material: {complete_product_info.get('material', 'Not found')}")
                        print(f"   Article Number: {complete_product_info.get('article_number', 'Not found')}")
                        print(f"   Packshot Image: {'✅ Found' if complete_product_info.get('packshot_found') else '❌ Not found'}")
                        print(f"   Color Extraction: {'✅ Success' if complete_product_info.get('color_extraction_success') else '❌ Failed'}")
                        if complete_product_info.get('dominant_tone'):
                            print(f"   Dominant Tone: {complete_product_info.get('dominant_tone')}")
                        if complete_product_info.get('dominant_hue'):
                            print(f"   Dominant Hue: {complete_product_info.get('dominant_hue')}")
                        if complete_product_info.get('color_count'):
                            print(f"   Total Colors: {complete_product_info.get('color_count')}")
                        if complete_product_info.get('neutral_colors'):
                            print(f"   Neutral Colors: {complete_product_info.get('neutral_colors')}")
                        
                    except Exception as e:
                        print(f"❌ Error processing product {i}: {str(e)}")
                        continue
                
            except Exception as e:
                print(f"Error processing clothing type {clothing_type}: {str(e)}")
                continue
        
        # Print final statistics
        print(f"\n{'='*60}")
        print("FINAL STATISTICS")
        print(f"{'='*60}")
        print(f"Total products processed: {total_products_processed}")
        print(f"Total products skipped (duplicates): {total_products_skipped}")
        print(f"Storage method: {'Database' if use_database else 'CSV'}")
        
        if use_database and db_client:
            # Get database statistics
            stats = db_client.get_database_stats()
            print(f"Database URL: {stats.get('database_url', 'Unknown')}")
            print(f"Total products in database: {stats.get('total_products', 0)}")
        
        return total_products_processed
        
    finally:
        driver.quit()

def get_specific_clothing_types_detailed_data(clothing_types, items_per_type=3):
    """
    Fetch detailed product information from specific clothing types
    
    Args:
        clothing_types (list): List of clothing types to process
        items_per_type (int): Number of items to fetch per clothing type
    
    Returns:
        list: List of dictionaries containing detailed product information
    """
    all_products_data = []
    
    # Initialize webdriver
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Firefox(options=options)
    
    try:
        # Process each specified clothing type
        for clothing_type in clothing_types:
            print(f"\n{'='*60}")
            print(f"Processing clothing type: {clothing_type}")
            print(f"{'='*60}")
            
            try:
                # Get products for this clothing type
                products = get_zalando_products(clothing_type, max_items=items_per_type)
                
                if not products:
                    print(f"No products found for {clothing_type}")
                    continue
                
                print(f"Found {len(products)} products for {clothing_type}")
                
                # Process each product to get detailed information
                for i, product in enumerate(products, 1):
                    print(f"\nProcessing product {i}/{len(products)}: {product['name'][:50]}...")
                    
                    # Extract detailed information from product page
                    detailed_info = extract_product_details_from_page(driver, product['url'])
                    
                    # Get packshot image for better color analysis
                    print(f"  Finding packshot image for color analysis...")
                    packshot_img_url = find_packshot_image(product['url'], driver)
                    
                    # Use packshot image if found, otherwise try to modify the original image URL
                    if packshot_img_url:
                        final_img_url = packshot_img_url
                        packshot_found = True
                        print(f"  ✅ Found packshot image: {packshot_img_url}")
                    else:
                        # Try to modify the original image URL to get packshot
                        modified_img_url = modify_image_url_to_packshot(product['image_url'])
                        if modified_img_url != product['image_url']:
                            final_img_url = modified_img_url
                            packshot_found = True
                            print(f"  🔄 Modified image URL to packshot: {modified_img_url}")
                        else:
                            # Use the original image as fallback
                            final_img_url = product['image_url']
                            packshot_found = False
                            print(f"  ⚠️ Using original image (no packshot available): {product['image_url']}")
                    
                    # Extract colors from the packshot image
                    print(f"  Extracting colors from {'packshot' if packshot_found else 'original'} image...")
                    color_data = extract_colors_from_product_image(final_img_url)
                    
                    # Combine basic product info with detailed info and color data
                    complete_product_info = {
                        'clothing_type': clothing_type,
                        'name': product['name'],
                        'url': product['url'],
                        'original_url': product['url'],  # Keep original URL
                        'image_url': final_img_url,  # Use packshot image if available
                        'original_image_url': product['image_url'],  # Keep original image URL for reference
                        'packshot_found': packshot_found,
                        'price': product['price'],
                        'material': detailed_info['material'],
                        'description': detailed_info['description'],
                        'article_number': detailed_info['article_number'],
                        'manufacturing_info': detailed_info['manufacturing_info'],
                        # Color information
                        'dominant_color_hex': color_data['summary'].get('dominant_color', {}).get('hex', ''),
                        'dominant_color_rgb': color_data['summary'].get('dominant_color', {}).get('rgb', ''),
                        'dominant_tone': color_data['summary'].get('dominant_color', {}).get('css_color', ''),
                        'dominant_hue': color_data['summary'].get('dominant_color', {}).get('css_color', ''),
                        'dominant_shade': color_data['summary'].get('dominant_color', {}).get('css_color', ''),
                        'overall_tone': color_data['summary'].get('overall_css_color', ''),
                        'overall_hue': color_data['summary'].get('overall_css_color', ''),
                        'overall_shade': color_data['summary'].get('overall_css_color', ''),
                        'color_count': color_data['summary'].get('color_count', 0),
                        'neutral_colors': color_data['summary'].get('neutral_colors', 0),
                        'color_extraction_success': color_data['success']
                    }
                    
                    all_products_data.append(complete_product_info)
                    print(f"✅ Completed product {i}")
                
            except Exception as e:
                print(f"Error processing clothing type {clothing_type}: {str(e)}")
                continue
        
        return all_products_data
        
    finally:
        driver.quit()

def main():
    """
    Main function to collect detailed product data from specific clothing types
    """
    print("="*80)
    print("ZALANDO DETAILED PRODUCT COLLECTOR WITH SUPABASE")
    print("="*80)
    print("This script will:")
    print("1. Go through shirts, t_shirts, and shorts")
    print("2. Fetch top N items for each type")
    print("3. Visit each product page to extract detailed information")
    print("4. Check for existing products in Supabase database")
    print("5. Save new products to database (or CSV as fallback)")
    print("6. Show progress in real-time")
    print("="*80)
    
    # Define the clothing types to collect
    clothing_types_to_collect = ['shirts', 't_shirts', 'shorts']
    
    # Get user input for number of items per type
    try:
        items_per_type = int(input("Enter number of items to fetch per clothing type (default: 3): ") or "3")
    except ValueError:
        items_per_type = 3
        print("Invalid input, using default value: 3")
    
    # Ask user for storage method
    print("\nChoose storage method:")
    print("1. Supabase Database (recommended)")
    print("2. CSV File (fallback)")
    
    try:
        storage_choice = int(input("Enter choice (1 or 2, default: 1): ") or "1")
        use_database = (storage_choice == 1)
    except ValueError:
        use_database = True
        print("Invalid input, using default: Supabase Database")
    
    # Ask user for processing mode
    print("\nChoose processing mode:")
    print("1. Individual processing (save each product immediately)")
    print("2. Bulk processing (collect all products first, then save)")
    
    try:
        mode_choice = int(input("Enter choice (1 or 2, default: 1): ") or "1")
    except ValueError:
        mode_choice = 1
        print("Invalid input, using default: Individual processing")
    
    print(f"\nWill fetch {items_per_type} items per clothing type for: {', '.join(clothing_types_to_collect)}")
    print(f"Storage method: {'Supabase Database' if use_database else 'CSV File'}")
    print("This may take a while as it visits each product page...")
    
    if use_database:
        print("\n⚠️ Make sure you have set the SUPABASE_KEY environment variable!")
        print("   Example: export SUPABASE_KEY='your-supabase-anon-key'")
    
    # Confirm before proceeding
    confirm = input("\nProceed? (y/N): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("Operation cancelled.")
        return
    
    try:
        if mode_choice == 1:
            # Individual processing mode
            print("\nStarting individual product processing...")
            print("Each product will be saved immediately after processing.")
            
            total_processed = get_specific_clothing_types_detailed_data_individual(
                clothing_types_to_collect, 
                items_per_type=items_per_type,
                use_database=use_database
            )
            
            if total_processed > 0:
                print(f"\n✅ Successfully processed and saved {total_processed} products")
                if use_database:
                    print("📊 Check your Supabase database for results")
                else:
                    print("📁 Check the generated CSV file for results")
            else:
                print("No new products were processed (all may have been duplicates)")
                
        else:
            # Bulk processing mode (original behavior)
            print("\nStarting bulk data collection...")
            detailed_products = get_specific_clothing_types_detailed_data(
                clothing_types_to_collect, 
                items_per_type=items_per_type
            )
            
            if not detailed_products:
                print("No detailed product data collected")
                return
            
            print(f"\n✅ Successfully collected data for {len(detailed_products)} products")
            
            # Create and display table
            print("\n" + "="*80)
            print("PRODUCT DETAILS TABLE")
            print("="*80)
            table = create_product_table(detailed_products)
            print(table)
            
            # Save to CSV (bulk mode always uses CSV for now)
            filename = f'zalando_detailed_products_{items_per_type}_per_type.csv'
            save_products_to_csv(detailed_products, filename)
            
            # Show summary statistics
            print(f"\n" + "="*50)
            print("SUMMARY STATISTICS")
            print("="*50)
            
            # Count by clothing type
            type_counts = {}
            for product in detailed_products:
                clothing_type = product['clothing_type']
                type_counts[clothing_type] = type_counts.get(clothing_type, 0) + 1
            
            print("Products by clothing type:")
            for clothing_type, count in sorted(type_counts.items()):
                print(f"  {clothing_type}: {count} products")
            
            # Count products with material information
            products_with_material = sum(1 for p in detailed_products if p.get('material'))
            print(f"\nProducts with material info: {products_with_material}/{len(detailed_products)} ({products_with_material/len(detailed_products)*100:.1f}%)")
            
            # Count products with article numbers
            products_with_article = sum(1 for p in detailed_products if p.get('article_number'))
            print(f"Products with article numbers: {products_with_article}/{len(detailed_products)} ({products_with_article/len(detailed_products)*100:.1f}%)")
            
            # Count products with descriptions
            products_with_description = sum(1 for p in detailed_products if p.get('description'))
            print(f"Products with descriptions: {products_with_description}/{len(detailed_products)} ({products_with_description/len(detailed_products)*100:.1f}%)")
            
            # Packshot image statistics
            print(f"\n" + "="*30)
            print("PACKSHOT IMAGE STATISTICS")
            print("="*30)
            
            # Count products with packshot images
            products_with_packshot = sum(1 for p in detailed_products if p.get('packshot_found'))
            print(f"Products with packshot images: {products_with_packshot}/{len(detailed_products)} ({products_with_packshot/len(detailed_products)*100:.1f}%)")
            
            # Color analysis statistics
            print(f"\n" + "="*30)
            print("COLOR ANALYSIS STATISTICS")
            print("="*30)
            
            # Count successful color extractions
            successful_color_extractions = sum(1 for p in detailed_products if p.get('color_extraction_success'))
            print(f"Successful color extractions: {successful_color_extractions}/{len(detailed_products)} ({successful_color_extractions/len(detailed_products)*100:.1f}%)")
            
            # Analyze dominant tones
            tone_counts = {}
            for product in detailed_products:
                if product.get('dominant_tone'):
                    tone = product['dominant_tone']
                    tone_counts[tone] = tone_counts.get(tone, 0) + 1
            
            if tone_counts:
                print(f"\nDominant tones distribution:")
                for tone, count in sorted(tone_counts.items()):
                    print(f"  {tone}: {count} products ({count/len(detailed_products)*100:.1f}%)")
            
            # Analyze dominant hues
            hue_counts = {}
            for product in detailed_products:
                if product.get('dominant_hue'):
                    hue = product['dominant_hue']
                    hue_counts[hue] = hue_counts.get(hue, 0) + 1
            
            if hue_counts:
                print(f"\nDominant hues distribution:")
                for hue, count in sorted(hue_counts.items()):
                    print(f"  {hue}: {count} products ({count/len(detailed_products)*100:.1f}%)")
            
            # Analyze dominant shades
            shade_counts = {}
            for product in detailed_products:
                if product.get('dominant_shade'):
                    shade = product['dominant_shade']
                    shade_counts[shade] = shade_counts.get(shade, 0) + 1
            
            if shade_counts:
                print(f"\nDominant shades distribution:")
                for shade, count in sorted(shade_counts.items()):
                    print(f"  {shade}: {count} products ({count/len(detailed_products)*100:.1f}%)")
            
            # Average color count
            color_counts = [p.get('color_count', 0) for p in detailed_products if p.get('color_count')]
            if color_counts:
                avg_colors = sum(color_counts) / len(color_counts)
                print(f"\nAverage colors per product: {avg_colors:.1f}")
            
            # Neutral colors analysis
            neutral_colors = [p.get('neutral_colors', 0) for p in detailed_products if p.get('neutral_colors')]
            if neutral_colors:
                products_with_neutrals = sum(1 for n in neutral_colors if n > 0)
                print(f"Products with neutral colors: {products_with_neutrals}/{len(detailed_products)} ({products_with_neutrals/len(detailed_products)*100:.1f}%)")
            
            print(f"\n✅ Data collection completed successfully!")
            print(f"📁 Results saved to: {filename}")
        
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during data collection: {str(e)}")

if __name__ == "__main__":
    main() 