# create a function that takes a number of parameters and searches the Supabase database with filters
#  example of how it would be used:
# I want a blue crewneck sweater 
# Then the function would take filters as inputs such as color blue and type of clothing is sweater
# the function would then return the products matching the filters

# the function would use the supabase_db.py file to search the database with the filters
# the function would return the products

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_collection'))

from supabase_db import SupabaseDB
from allowed_tags import DESCRIPTIVE_TAGS, CLOTHING_TYPES, COLORS
import re
from tqdm import tqdm
from typing import List, Dict, Optional, Any, Set, Tuple
import uuid

ALLOWED_TAGS = set(DESCRIPTIVE_TAGS + CLOTHING_TYPES + COLORS)
PRODUCT_CACHE = None

def extract_price(price_str):
    """
    Extract numeric price from price string (e.g., '499,00 kr' -> 499.0)
    
    Args:
        price_str (str): Price string from Zalando (e.g., '499,00 kr', '1 299,00 kr')
    
    Returns:
        float: Extracted price value, or float('inf') if price is not available
    """
    if not price_str or price_str == "Price not available":
        return float('inf')
    
    try:
        # Remove 'kr' and any whitespace
        price = price_str.replace('kr', '').strip()
        # Replace comma with dot for decimal point
        price = price.replace(',', '.')
        # Remove any spaces (for thousands separator)
        price = price.replace(' ', '')
        return float(price)
    except ValueError:
        return float('inf')

def calculate_product_relevance_score(product: Dict[str, Any], 
                                    target_tags: Optional[List[str]] = None,
                                    weights: Optional[Dict[str, float]] = None) -> float:
    """
    Calculate a relevance score for a product based solely on tag matches.
    Args:
        product (Dict[str, Any]): Product dictionary with all product information
        target_tags (List[str], optional): List of tags to match against
    Returns:
        float: Relevance score between 0 and 100 (higher is better)
    """
    if not target_tags or len(target_tags) == 0:
        return 0.0
    searchable_text = f"{product.get('name', '')} {product.get('description', '')} {product.get('material', '')}".lower()
    tag_matches = [tag for tag in target_tags if tag.lower() in searchable_text]
    score = (len(tag_matches) / len(target_tags)) * 100 if target_tags else 0.0
    return score

def load_all_products_from_supabase():
    """
    Loads all products from Supabase into the global PRODUCT_CACHE.
    """
    global PRODUCT_CACHE
    db_client = SupabaseDB()
    query = db_client.client.table('clothes_db').select('*')
    try:
        response = query.execute()
        PRODUCT_CACHE = response.data
    except Exception as e:
        raise Exception(f"Failed to load products from Supabase: {str(e)}")

def refresh_product_cache():
    """
    Refreshes the product cache by reloading all products from Supabase.
    """
    load_all_products_from_supabase()

def search_database_products(
                           max_items: int = 20000, 
                           sort_by_price: bool = False, price_order: str = 'asc',
                           use_relevance_scoring: bool = True,
                           scoring_weights: Optional[Dict[str, float]] = None,
                           target_tags: Optional[List[str]] = None
                           , clothing_type: Optional[List[str]] = None
                           , color: Optional[List[str]] = None) -> List[Dict]:
    """
    Search products in the Supabase database using only the Tags column.
    Clothing type and color tags are required (must match), all other tags are used for scoring.
    """
    global PRODUCT_CACHE
    if PRODUCT_CACHE is None:
        load_all_products_from_supabase()
    else:
        load_all_products_from_supabase()
    # Use input parameters directly for clothing type and color
    clothing_type_tags = clothing_type if isinstance(clothing_type, list) else [clothing_type] if clothing_type else []
    color_tags = color if isinstance(color, list) else [color] if color else []
    other_tags = [tag for tag in (target_tags or []) if tag not in (clothing_type_tags + color_tags)]
    if not clothing_type_tags or not color_tags:
        return []
    products = []
    for item in PRODUCT_CACHE:
        product_tags = item.get('Tags', []) or []
        has_clothing_type = any(ct.lower() in [t.lower() for t in product_tags] for ct in clothing_type_tags)
        has_color = any(c.lower() in [t.lower() for t in product_tags] for c in color_tags)
        if not (has_clothing_type and has_color):
            continue
        if other_tags:
            match_count = len([tag for tag in other_tags if tag.lower() in [t.lower() for t in product_tags]])
            relevance_score = (match_count / len(other_tags)) * 100 if other_tags else 0.0
        else:
            relevance_score = 0.0
        price_numeric = extract_price(item.get('price', ''))
        product = {
            'id': item.get('id') if item.get('id') is not None else str(uuid.uuid4()),
            'name': item.get('name'),
            'url': item.get('url'),
            'original_url': item.get('original_url'),
            'image_url': item.get('image_url'),
            'original_image_url': item.get('original_image_url'),
            'price': item.get('price'),
            'price_numeric': price_numeric,
            'clothing_type': item.get('clothing_type'),
            'material': item.get('material'),
            'description': item.get('description'),
            'article_number': item.get('article_number'),
            'manufacturing_info': item.get('manufacturing_info'),
            'dominant_color_hex': item.get('dominant_color_hex'),
            'dominant_color_rgb': item.get('dominant_color_rgb'),
            'dominant_tone': item.get('dominant_tone'),
            'dominant_hue': item.get('dominant_hue'),
            'dominant_shade': item.get('dominant_shade'),
            'overall_tone': item.get('overall_tone'),
            'overall_hue': item.get('overall_hue'),
            'overall_shade': item.get('overall_shade'),
            'color_count': item.get('color_count'),
            'neutral_colors': item.get('neutral_colors'),
            'color_extraction_success': item.get('color_extraction_success'),
            'packshot_found': item.get('packshot_found'),
            'Tags': product_tags,
            'relevance_score': relevance_score
        }
        products.append(product)
    # Sort by relevance score, then price if requested
    if use_relevance_scoring:
        if sort_by_price:
            products.sort(key=lambda x: (-x['relevance_score'], x['price_numeric'] if price_order == 'asc' else -x['price_numeric']))
        else:
            products.sort(key=lambda x: x['relevance_score'], reverse=True)
    else:
        if sort_by_price:
            products.sort(key=lambda x: x['price_numeric'], reverse=(price_order == 'desc'))
    return products[:max_items]

if __name__ == '__main__':
    # Example manual test for search_database_products
    # NOTE: This will attempt to connect to the real database. Adjust parameters as needed.
    print("Testing search_database_products with example tags...")
    example_tags = ["summer"]
    CLOTHING_TYPES = ['shorts', "jeans"]
    COLORS = ['black',"white"]
    try:
        results = search_database_products(
            target_tags=example_tags,
            max_items=5000,
            sort_by_price=True,
            price_order='asc',
            use_relevance_scoring=True,
            clothing_type=CLOTHING_TYPES,
            color=COLORS
        )
        print(f"Results for tags {example_tags} (top 5 shown):")
        for i, product in enumerate(results[:5], 1):
            print(f"\nResult #{i}:")
            print(f"  Name: {product.get('name')}")
            print(f"  Price: {product.get('price')}")
            print(f"  URL: {product.get('url')}")
            print(f"  Image URL: {product.get('image_url')}")
            print(f"  Clothing Type: {product.get('clothing_type')}")
            print(f"  Material: {product.get('material')}")
            print(f"  Description: {product.get('description')}")
            print(f"  Tags: {product.get('Tags')}")
            print(f"  Relevance Score: {product.get('relevance_score'):.2f}")
    except Exception as e:
        print(f"Error during search: {e}")

