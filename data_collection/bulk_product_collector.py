#!/usr/bin/env python3
"""
Bulk Product Collector for Zalando

This script automatically collects 100 items from all clothing types
and uploads them to Supabase in batches of 20 for efficiency and data safety.
No user input required - runs completely automatically.
"""

from zalando_scraper import (
    get_zalando_products,
    extract_product_details_from_page,
    find_packshot_image,
    modify_image_url_to_packshot
)
from color_extractor import extract_colors_from_product_image
from supabase_db import SupabaseDB
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import os
import sys
from datetime import datetime
from tqdm import tqdm

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# All available clothing types from zalando_scraper
ALL_CLOTHING_TYPES = [
    't_shirts', 'shirts', 'sweaters', 'pants', 'jeans', 'shorts',
    'jackets', 'knitwear', 'sportswear', 'tracksuits', 'suits',
    'coats', 'underwear', 'swimwear', 'loungewear', 'outlet'
]

class ProgressManager:
    """Manages all progress bars and status updates for clean terminal output"""
    
    def __init__(self):
        self.main_pbar = None
        self.current_pbar = None
        self.status_text = ""
        
    def start_main_progress(self, total_clothing_types, items_per_type, batch_size):
        """Initialize the main progress bar"""
        total_items = total_clothing_types * items_per_type
        self.main_pbar = tqdm(
            total=total_items,
            desc="🚀 Bulk Collection",
            unit="product",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}',
            position=0,
            leave=True
        )
        self.update_status(f"Target: {items_per_type} items/type, Batch: {batch_size}")
        
    def start_clothing_type_progress(self, clothing_type, items_count):
        """Start progress for a specific clothing type"""
        if self.current_pbar:
            self.current_pbar.close()
        
        self.current_pbar = tqdm(
            total=items_count,
            desc=f"👕 {clothing_type}",
            unit="item",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {postfix}',
            position=1,
            leave=False
        )
        
    def update_main_progress(self, n=1, postfix=None):
        """Update the main progress bar"""
        if self.main_pbar:
            if postfix:
                self.main_pbar.set_postfix_str(postfix)
            self.main_pbar.update(n)
            
    def update_clothing_type_progress(self, n=1, postfix=None):
        """Update the clothing type progress bar"""
        if self.current_pbar:
            if postfix:
                self.current_pbar.set_postfix_str(postfix)
            self.current_pbar.update(n)
            
    def update_status(self, status):
        """Update the status text in the main progress bar"""
        self.status_text = status
        if self.main_pbar:
            self.main_pbar.set_postfix_str(status)
            
    def write_status(self, message):
        """Write a status message without interfering with progress bars"""
        if self.main_pbar:
            tqdm.write(message)
        else:
            pass
            
    def close_all(self):
        """Close all progress bars"""
        if self.current_pbar:
            self.current_pbar.close()
        if self.main_pbar:
            self.main_pbar.close()

def save_batch_to_database(batch_data, db_client, batch_number, progress_manager):
    """
    Save a batch of products to Supabase database
    
    Args:
        batch_data (list): List of product data dictionaries
        db_client (SupabaseDB): Database client instance
        batch_number (int): Current batch number for logging
        progress_manager (ProgressManager): Progress manager instance
    
    Returns:
        tuple: (success_count, failed_count)
    """
    success_count = 0
    failed_count = 0
    
    for i, product_data in enumerate(batch_data, 1):
        try:
            success = db_client.insert_product(product_data)
            if success:
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
    
    return success_count, failed_count

def process_single_product(driver, product, clothing_type, progress_manager):
    """
    Process a single product to extract detailed information and colors
    
    Args:
        driver: Selenium WebDriver instance
        product (dict): Basic product information
        clothing_type (str): Type of clothing
        progress_manager (ProgressManager): Progress manager instance
    
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
        'original_url': product['url'],
        'image_url': final_img_url,
        'original_image_url': product['image_url'],
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

def collect_all_products_batch_upload(items_per_type=1000, batch_size=20):
    """
    Collect products from all clothing types and upload to Supabase in batches
    
    Args:
        items_per_type (int): Number of items to fetch per clothing type
        batch_size (int): Number of products to upload per batch
    
    Returns:
        dict: Statistics about the collection process
    """
    progress_manager = ProgressManager()
    
    try:
        # Initialize database client
        try:
            db_client = SupabaseDB()
            existing_urls = db_client.get_existing_product_urls()
        except Exception as e:
            return None
        
        # Initialize webdriver
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Firefox(options=options)
        
        # Statistics tracking
        stats = {
            'total_processed': 0,
            'total_skipped': 0,
            'total_saved': 0,
            'total_failed': 0,
            'batches_uploaded': 0,
            'clothing_type_stats': {},
            'start_time': datetime.now(),
            'errors': []
        }
        
        current_batch = []
        batch_number = 1
        
        # Start main progress bar
        progress_manager.start_main_progress(len(ALL_CLOTHING_TYPES), items_per_type, batch_size)
        
        # Process each clothing type
        for clothing_type in ALL_CLOTHING_TYPES:
            clothing_type_stats = {
                'processed': 0,
                'skipped': 0,
                'saved': 0,
                'failed': 0
            }
            
            try:
                # Get products for this clothing type
                products = get_zalando_products(clothing_type, max_items=items_per_type)
                
                if not products:
                    stats['clothing_type_stats'][clothing_type] = clothing_type_stats
                    continue
                
                # Start clothing type progress bar
                progress_manager.start_clothing_type_progress(clothing_type, len(products))
                
                # Process each product
                for i, product in enumerate(products, 1):
                    # Check if product URL already exists in database
                    if product['url'] in existing_urls:
                        stats['total_skipped'] += 1
                        clothing_type_stats['skipped'] += 1
                        progress_manager.update_clothing_type_progress(1, f"Skipped: {clothing_type_stats['skipped']}")
                        continue
                    
                    try:
                        # Process the product
                        complete_product_info = process_single_product(driver, product, clothing_type, progress_manager)
                        
                        # Add to current batch
                        current_batch.append(complete_product_info)
                        stats['total_processed'] += 1
                        clothing_type_stats['processed'] += 1
                        
                        progress_manager.update_clothing_type_progress(1, f"Processed: {clothing_type_stats['processed']}")
                        progress_manager.update_main_progress(1, f"Total: {stats['total_processed']}")
                        
                        # Upload batch if it reaches the batch size
                        if len(current_batch) >= batch_size:
                            success_count, failed_count = save_batch_to_database(
                                current_batch, db_client, batch_number, progress_manager
                            )
                            
                            stats['total_saved'] += success_count
                            stats['total_failed'] += failed_count
                            clothing_type_stats['saved'] += success_count
                            clothing_type_stats['failed'] += failed_count
                            stats['batches_uploaded'] += 1
                            
                            # Clear the batch
                            current_batch = []
                            batch_number += 1
                            
                            # Small delay between batches
                            time.sleep(2)
                        
                    except Exception as e:
                        error_msg = f"Error processing product {i} in {clothing_type}: {str(e)}"
                        stats['errors'].append(error_msg)
                        clothing_type_stats['failed'] += 1
                        progress_manager.update_clothing_type_progress(1, f"Failed: {clothing_type_stats['failed']}")
                        continue
                
                # Store clothing type statistics
                stats['clothing_type_stats'][clothing_type] = clothing_type_stats
                
            except Exception as e:
                error_msg = f"Error processing clothing type {clothing_type}: {str(e)}"
                stats['errors'].append(error_msg)
                stats['clothing_type_stats'][clothing_type] = clothing_type_stats
                continue
        
        # Upload any remaining products in the final batch
        if current_batch:
            success_count, failed_count = save_batch_to_database(
                current_batch, db_client, batch_number, progress_manager
            )
            
            stats['total_saved'] += success_count
            stats['total_failed'] += failed_count
            stats['batches_uploaded'] += 1
        
        # Calculate final statistics
        stats['end_time'] = datetime.now()
        stats['duration'] = stats['end_time'] - stats['start_time']
        
        return stats
        
    finally:
        progress_manager.close_all()
        driver.quit()

def print_final_statistics(stats):
    """
    Print comprehensive final statistics
    
    Args:
        stats (dict): Statistics dictionary from collection process
    """
    if not stats:
        return
    
    # Statistics are now handled silently - no print statements needed

def main():
    """
    Main function - runs the bulk collection automatically
    """
    # Check if required API keys are set
    missing_keys = Config.validate_required_keys()
    if missing_keys:
        print("❌ Missing required API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\n💡 To fix this:")
        print("   1. Create a .env file in the project root")
        print("   2. Add your API keys to the .env file")
        print("   3. Or set them as environment variables")
        print("\nExample .env file content:")
        print("SUPABASE_KEY=your_supabase_anon_key_here")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        return
    
    try:
        # Run the bulk collection
        stats = collect_all_products_batch_upload(
            items_per_type=100,
            batch_size=20
        )
        
        # Print final statistics
        print_final_statistics(stats)
        
    except KeyboardInterrupt:
        print("\n⚠️  Collection interrupted by user")
    except Exception as e:
        print(f"❌ Error during bulk collection: {str(e)}")

if __name__ == "__main__":
    main() 