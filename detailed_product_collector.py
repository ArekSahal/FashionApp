#!/usr/bin/env python3
"""
Detailed Product Collector for Zalando

This script collects detailed product information including:
- Material composition
- Article numbers
- Packshot images for better color analysis
- Color extraction from images
- Manufacturing information

It can save to either Supabase database or CSV file.
"""

from data_collection.zalando_scraper import (
    get_zalando_products,
    extract_product_details_from_page,
    find_packshot_image,
    modify_image_url_to_packshot
)
from data_collection.color_extractor import extract_colors_from_product_image
from data_collection.supabase_db import SupabaseDB
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import csv
import os
from datetime import datetime

def save_to_database(product_data, db_client):
    """Save a single product to Supabase database"""
    try:
        success = db_client.insert_product(product_data)
        if success:
            return True
        else:
            return False
    except Exception as e:
        return False

def save_to_csv(product_data, filename="detailed_products.csv"):
    """Save a single product to CSV file"""
    try:
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'clothing_type', 'name', 'url', 'image_url', 'price',
                'material', 'description', 'article_number', 'manufacturing_info',
                'packshot_found', 'dominant_color_hex', 'dominant_color_rgb',
                'dominant_tone', 'dominant_hue', 'dominant_shade',
                'overall_tone', 'overall_hue', 'overall_shade',
                'color_count', 'neutral_colors', 'color_extraction_success'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(product_data)
        
        return True
    except Exception as e:
        return False

def process_single_product(driver, product, clothing_type, save_function, save_args):
    """
    Process a single product to extract detailed information and colors
    
    Args:
        driver: Selenium WebDriver instance
        product (dict): Basic product information
        clothing_type (str): Type of clothing
        save_function: Function to save the product (database or CSV)
        save_args: Arguments for the save function
    
    Returns:
        dict: Complete product information with details and colors
    """
    # Extract detailed information from product page
    detailed_info = extract_product_details_from_page(driver, product['url'])
    
    # Get packshot image for better color analysis
    packshot_img_url = find_packshot_image(product['url'], driver)
    
    # Use packshot image if found, otherwise try to modify the original image URL
    if packshot_img_url:
        final_img_url = packshot_img_url
        packshot_found = True
    else:
        # Try to modify the original image URL to get packshot
        modified_img_url = modify_image_url_to_packshot(product['image_url'])
        if modified_img_url != product['image_url']:
            final_img_url = modified_img_url
            packshot_found = True
        else:
            # Use the original image as fallback
            final_img_url = product['image_url']
            packshot_found = False
    
    # Extract colors from the image
    color_data = extract_colors_from_product_image(final_img_url)
    
    # Combine basic product info with detailed info and color data
    complete_product_info = {
        'clothing_type': clothing_type,
        'name': product['name'],
        'url': product['url'],
        'image_url': final_img_url,
        'price': product['price'],
        'material': detailed_info['material'],
        'description': detailed_info['description'],
        'article_number': detailed_info['article_number'],
        'manufacturing_info': detailed_info['manufacturing_info'],
        'packshot_found': packshot_found,
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
    
    # Save the product
    save_function(complete_product_info, *save_args)
    
    return complete_product_info

def collect_detailed_products_individual(clothing_types_to_collect, items_per_type=3, use_database=True):
    """
    Collect detailed product information and save each product immediately
    
    Args:
        clothing_types_to_collect (list): List of clothing types to collect
        items_per_type (int): Number of items to fetch per clothing type
        use_database (bool): Whether to use database or CSV storage
    
    Returns:
        dict: Statistics about the collection process
    """
    # Initialize storage
    if use_database:
        try:
            db_client = SupabaseDB()
            existing_urls = db_client.get_existing_product_urls()
            save_function = save_to_database
            save_args = (db_client,)
        except Exception as e:
            # Fall back to CSV if database fails
            use_database = False
            save_function = save_to_csv
            save_args = ()
    else:
        save_function = save_to_csv
        save_args = ()
    
    # Initialize webdriver
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Firefox(options=options)
    
    # Statistics tracking
    total_products_processed = 0
    total_products_skipped = 0
    
    try:
        # Process each clothing type
        for clothing_type in clothing_types_to_collect:
            # Get products for this clothing type
            products = get_zalando_products(clothing_type, max_items=items_per_type)
            
            if not products:
                continue
            
            # Process each product
            for i, product in enumerate(products, 1):
                # Check if product URL already exists in database (if using database)
                if use_database and product['url'] in existing_urls:
                    total_products_skipped += 1
                    continue
                
                try:
                    # Process and save the product
                    complete_product_info = process_single_product(
                        driver, product, clothing_type, save_function, save_args
                    )
                    
                    total_products_processed += 1
                    
                except Exception as e:
                    continue
        
        # Get final statistics
        stats = {
            'total_processed': total_products_processed,
            'total_skipped': total_products_skipped,
            'storage_method': 'Database' if use_database else 'CSV'
        }
        
        if use_database:
            try:
                db_stats = db_client.get_database_stats()
                stats['database_url'] = db_stats.get('database_url', 'Unknown')
                stats['total_products'] = db_stats.get('total_products', 0)
            except:
                pass
        
        return stats
        
    finally:
        driver.quit()

def collect_detailed_products_bulk(clothing_types_to_collect, items_per_type=3):
    """
    Collect detailed product information and return as a list (no immediate saving)
    
    Args:
        clothing_types_to_collect (list): List of clothing types to collect
        items_per_type (int): Number of items to fetch per clothing type
    
    Returns:
        list: List of detailed product information dictionaries
    """
    # Initialize webdriver
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Firefox(options=options)
    
    detailed_products = []
    
    try:
        # Process each clothing type
        for clothing_type in clothing_types_to_collect:
            # Get products for this clothing type
            products = get_zalando_products(clothing_type, max_items=items_per_type)
            
            if not products:
                continue
            
            # Process each product
            for i, product in enumerate(products, 1):
                try:
                    # Extract detailed information from product page
                    detailed_info = extract_product_details_from_page(driver, product['url'])
                    
                    # Get packshot image for better color analysis
                    packshot_img_url = find_packshot_image(product['url'], driver)
                    
                    # Use packshot image if found, otherwise try to modify the original image URL
                    if packshot_img_url:
                        final_img_url = packshot_img_url
                        packshot_found = True
                    else:
                        # Try to modify the original image URL to get packshot
                        modified_img_url = modify_image_url_to_packshot(product['image_url'])
                        if modified_img_url != product['image_url']:
                            final_img_url = modified_img_url
                            packshot_found = True
                        else:
                            # Use the original image as fallback
                            final_img_url = product['image_url']
                            packshot_found = False
                    
                    # Extract colors from the image
                    color_data = extract_colors_from_product_image(final_img_url)
                    
                    # Combine basic product info with detailed info and color data
                    complete_product_info = {
                        'clothing_type': clothing_type,
                        'name': product['name'],
                        'url': product['url'],
                        'image_url': final_img_url,
                        'price': product['price'],
                        'material': detailed_info['material'],
                        'description': detailed_info['description'],
                        'article_number': detailed_info['article_number'],
                        'manufacturing_info': detailed_info['manufacturing_info'],
                        'packshot_found': packshot_found,
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
                    
                    detailed_products.append(complete_product_info)
                    
                except Exception as e:
                    continue
        
        return detailed_products
        
    finally:
        driver.quit()

def main():
    """
    Main function - interactive product collection
    """
    # Default clothing types to collect
    clothing_types_to_collect = ['shirts', 't_shirts', 'shorts']
    
    # Get user input for number of items per type
    try:
        items_per_type = int(input(f"Enter number of items per clothing type (default: 3): ") or "3")
    except ValueError:
        items_per_type = 3
    
    # Get user input for storage method
    try:
        storage_choice = input("\nChoose storage method:\n1. Supabase Database (recommended)\n2. CSV File (fallback)\nEnter choice (1 or 2): ") or "1"
        use_database = storage_choice == "1"
    except:
        use_database = True
    
    # Get user input for processing mode
    try:
        mode_choice = input("\nChoose processing mode:\n1. Individual processing (save each product immediately)\n2. Bulk processing (collect all products first, then save)\nEnter choice (1 or 2): ") or "1"
        individual_mode = mode_choice == "1"
    except:
        individual_mode = True
    
    # Check if Supabase key is set (if using database)
    if use_database and not os.getenv('SUPABASE_KEY'):
        return
    
    # Start collection based on mode
    if individual_mode:
        # Individual processing mode
        stats = collect_detailed_products_individual(
            clothing_types_to_collect, items_per_type, use_database
        )
        
        if stats and stats['total_processed'] > 0:
            if use_database:
                pass
            else:
                pass
        else:
            pass
    else:
        # Bulk processing mode
        detailed_products = collect_detailed_products_bulk(
            clothing_types_to_collect, items_per_type
        )
        
        if not detailed_products:
            pass
        else:
            # Create a summary table
            from tabulate import tabulate
            
            # Prepare data for table
            table_data = []
            for product in detailed_products[:10]:  # Show first 10 products
                table_data.append([
                    product['clothing_type'],
                    product['name'][:50] + "..." if len(product['name']) > 50 else product['name'],
                    product['material'][:30] + "..." if len(product.get('material', '')) > 30 else product.get('material', 'N/A'),
                    product.get('dominant_tone', 'N/A'),
                    product.get('color_count', 0),
                    '✅' if product.get('packshot_found') else '❌',
                    '✅' if product.get('color_extraction_success') else '❌'
                ])
            
            headers = ['Type', 'Name', 'Material', 'Dominant Color', 'Color Count', 'Packshot', 'Color Extraction']
            table = tabulate(table_data, headers=headers, tablefmt='grid')
            
            # Calculate summary statistics
            products_by_type = {}
            for product in detailed_products:
                clothing_type = product['clothing_type']
                if clothing_type not in products_by_type:
                    products_by_type[clothing_type] = 0
                products_by_type[clothing_type] += 1
            
            products_with_material = sum(1 for p in detailed_products if p.get('material') and p.get('material') != 'Not found')
            products_with_article = sum(1 for p in detailed_products if p.get('article_number') and p.get('article_number') != 'Not found')
            
            # Print summary
            if len(detailed_products) > 0:
                pass

if __name__ == "__main__":
    main() 