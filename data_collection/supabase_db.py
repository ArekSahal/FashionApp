#!/usr/bin/env python3
"""
Supabase Database Integration for Fashion App

This module handles all database operations for storing and retrieving
clothing product data from Supabase.
"""

import os
from supabase import create_client, Client
from typing import List, Dict, Optional, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseDB:
    """
    Supabase database client for clothes_db table operations
    """
    
    def __init__(self, url: str = "https://ohgyxtkvyffvycfpvxcq.supabase.co"):
        """
        Initialize Supabase client
        
        Args:
            url (str): Supabase project URL
        """
        self.url = url
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_key:
            raise ValueError("SUPABASE_KEY environment variable is required")
        
        try:
            self.client: Client = create_client(url, self.supabase_key)
            logger.info("✅ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {str(e)}")
            raise
    
    def get_existing_product_urls(self) -> Set[str]:
        """
        Get all existing product URLs from the database to avoid duplicates
        
        Returns:
            Set[str]: Set of existing product URLs
        """
        try:
            response = self.client.table('clothes_db').select('original_url').execute()
            
            if response.data:
                urls = {item['original_url'] for item in response.data if item.get('original_url')}
                logger.info(f"📊 Found {len(urls)} existing product URLs in database")
                return urls
            else:
                logger.info("📊 No existing products found in database")
                return set()
                
        except Exception as e:
            logger.error(f"❌ Error fetching existing URLs: {str(e)}")
            return set()
    
    def insert_product(self, product_data: Dict) -> bool:
        """
        Insert a single product into the database
        
        Args:
            product_data (Dict): Product data dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare data for insertion
            db_data = {
                'clothing_type': product_data.get('clothing_type', ''),
                'name': product_data.get('name', ''),
                'price': product_data.get('price', ''),
                'material': product_data.get('material', ''),
                'description': product_data.get('description', ''),
                'article_number': product_data.get('article_number', ''),
                'manufacturing_info': product_data.get('manufacturing_info', ''),
                'original_url': product_data.get('original_url', ''),
                'image_url': product_data.get('image_url', ''),
                'original_image_url': product_data.get('original_image_url', ''),
                'packshot_found': product_data.get('packshot_found', False),
                'dominant_color_hex': product_data.get('dominant_color_hex', ''),
                'dominant_color_rgb': product_data.get('dominant_color_rgb', ''),
                'dominant_tone': product_data.get('dominant_tone', ''),
                'dominant_hue': product_data.get('dominant_hue', ''),
                'dominant_shade': product_data.get('dominant_shade', ''),
                'overall_tone': product_data.get('overall_tone', ''),
                'overall_hue': product_data.get('overall_hue', ''),
                'overall_shade': product_data.get('overall_shade', ''),
                'color_count': product_data.get('color_count', 0),
                'neutral_colors': product_data.get('neutral_colors', 0),
                'color_extraction_success': product_data.get('color_extraction_success', False)
            }
            
            # Insert into database
            response = self.client.table('clothes_db').insert(db_data).execute()
            
            if response.data:
                logger.info(f"✅ Successfully inserted product: {product_data.get('name', 'Unknown')[:50]}...")
                return True
            else:
                logger.error(f"❌ Failed to insert product: {product_data.get('name', 'Unknown')[:50]}...")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error inserting product: {str(e)}")
            return False
    
    def insert_multiple_products(self, products_data: List[Dict]) -> Dict[str, int]:
        """
        Insert multiple products into the database
        
        Args:
            products_data (List[Dict]): List of product data dictionaries
            
        Returns:
            Dict[str, int]: Statistics about the insertion operation
        """
        success_count = 0
        error_count = 0
        
        logger.info(f"📦 Inserting {len(products_data)} products into database...")
        
        for product_data in products_data:
            if self.insert_product(product_data):
                success_count += 1
            else:
                error_count += 1
        
        stats = {
            'total': len(products_data),
            'successful': success_count,
            'failed': error_count,
            'success_rate': (success_count / len(products_data) * 100) if products_data else 0
        }
        
        logger.info(f"📊 Database insertion complete: {success_count}/{len(products_data)} successful ({stats['success_rate']:.1f}%)")
        
        return stats
    
    def get_products_by_type(self, clothing_type: str, limit: int = 100) -> List[Dict]:
        """
        Get products by clothing type
        
        Args:
            clothing_type (str): Type of clothing to retrieve
            limit (int): Maximum number of products to retrieve
            
        Returns:
            List[Dict]: List of product data
        """
        try:
            response = self.client.table('clothes_db').select('*').eq('clothing_type', clothing_type).limit(limit).execute()
            
            if response.data:
                logger.info(f"📊 Retrieved {len(response.data)} {clothing_type} products from database")
                return response.data
            else:
                logger.info(f"📊 No {clothing_type} products found in database")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error retrieving {clothing_type} products: {str(e)}")
            return []
    
    def get_all_products(self, limit: int = 1000) -> List[Dict]:
        """
        Get all products from the database
        
        Args:
            limit (int): Maximum number of products to retrieve
            
        Returns:
            List[Dict]: List of all product data
        """
        try:
            response = self.client.table('clothes_db').select('*').limit(limit).execute()
            
            if response.data:
                logger.info(f"📊 Retrieved {len(response.data)} products from database")
                return response.data
            else:
                logger.info("📊 No products found in database")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error retrieving products: {str(e)}")
            return []
    
    def get_database_stats(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Dict: Database statistics
        """
        try:
            # Get total count
            total_response = self.client.table('clothes_db').select('*', count='exact').execute()
            total_count = total_response.count if hasattr(total_response, 'count') else 0
            
            # Get count by clothing type
            type_stats = {}
            clothing_types = ['shirts', 't_shirts', 'shorts', 'jeans', 'jackets', 'tracksuits']
            
            for clothing_type in clothing_types:
                response = self.client.table('clothes_db').select('*', count='exact').eq('clothing_type', clothing_type).execute()
                count = response.count if hasattr(response, 'count') else 0
                type_stats[clothing_type] = count
            
            stats = {
                'total_products': total_count,
                'by_type': type_stats,
                'database_url': self.url
            }
            
            logger.info(f"📊 Database stats: {total_count} total products")
            for clothing_type, count in type_stats.items():
                if count > 0:
                    logger.info(f"   {clothing_type}: {count} products")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting database stats: {str(e)}")
            return {'error': str(e)}
    
    def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            bool: True if connection is successful
        """
        try:
            # Try to get database stats
            stats = self.get_database_stats()
            if 'error' not in stats:
                logger.info("✅ Database connection test successful")
                return True
            else:
                logger.error("❌ Database connection test failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {str(e)}")
            return False 