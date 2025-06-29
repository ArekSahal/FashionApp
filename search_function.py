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
from zalando_scraper import (
    CLOTHING_TYPES, 
    COLORS, 
    MATERIALS,
    validate_material
)
import re
from tqdm import tqdm
from typing import List, Dict, Optional, Any, Set, Tuple
import uuid




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

def search_database_products(filters: Optional[Dict] = None, 
                           max_items: int = 10, 
                           sort_by_price: bool = False, price_order: str = 'asc',
                           search_terms: Optional[List[str]] = None,
                           use_relevance_scoring: bool = True,
                           scoring_weights: Optional[Dict[str, float]] = None,
                           target_tags: Optional[List[str]] = None) -> List[Dict]:
    """
    Search products in the Supabase database using only the Tags column.
    Args:
        filters (dict, optional): Dictionary of filters to apply (e.g., {'material': 'linne', 'size': 'M'})
        max_items (int, optional): Maximum number of products to return. Defaults to 10.
        sort_by_price (bool, optional): Whether to sort results by price. Defaults to False.
        price_order (str, optional): Sort order for price ('asc' or 'desc'). Defaults to 'asc'.
        use_relevance_scoring (bool, optional): Whether to use the new relevance scoring system. Defaults to True.
        scoring_weights (Dict[str, float], optional): Custom weights for scoring components.
        search_terms (List[str], optional): List of key terms to search for in Tags column.
        target_tags (List[str], optional): Tags to use for scoring (new)
    Returns:
        list: List of dictionaries containing the products, sorted by relevance score or price.
    """
    if price_order not in ['asc', 'desc']:
        raise ValueError("price_order must be either 'asc' or 'desc'")
    try:
        db_client = SupabaseDB()
    except Exception as e:
        raise Exception(f"Failed to initialize database connection: {str(e)}")
    if filters is None:
        filters = {}
    # Use tags from target_tags or search_terms
    tags = target_tags if target_tags is not None else search_terms
    if not tags or len(tags) == 0:
        return []
    # Query for any product where Tags contains any of the input tags
    # Use the 'cs' (contains) operator for each tag and join with 'or'
    or_clauses = [f'Tags.cs.{{"{tag}"}}' for tag in tags if tag.strip()]
    query = db_client.client.table('clothes_db').select('*')
    if or_clauses:
        query = query.or_(','.join(or_clauses))
    query = query.limit(max_items * 100)  # Get more for better filtering
    try:
        response = query.execute()
    except Exception as e:
        raise Exception(f"Database query failed: {str(e)}")
    products = []
    for item in response.data:
        product_tags = item.get('Tags', []) or []
        # Score: number of input tags present in product's Tags / total input tags * 100
        match_count = len([tag for tag in tags if tag.lower() in [t.lower() for t in product_tags]])
        relevance_score = (match_count / len(tags)) * 100 if tags else 0.0
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
        # Only include products with at least one matching tag
        if match_count > 0:
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

def search_products_by_text(search_terms: List[str], max_items: int = 20, filters: Optional[Dict] = None,
                           sort_by_price: bool = False, price_order: str = 'asc',
                           use_relevance_scoring: bool = True,
                           scoring_weights: Optional[Dict[str, float]] = None) -> List[Dict]:
    """
    Advanced text search function that searches across multiple text columns in the database.
    This function is designed for more specific and flexible text-based searching.
    
    Args:
        search_terms (List[str]): List of key terms to search for
        max_items (int, optional): Maximum number of products to return. Defaults to 20.
        filters (dict, optional): Additional filters to apply
        sort_by_price (bool, optional): Whether to sort results by price. Defaults to False.
        price_order (str, optional): Sort order for price ('asc' or 'desc'). Defaults to 'asc'.
    
    Returns:
        List[Dict]: List of products matching the search criteria
    """
    if not search_terms or len(search_terms) == 0:
        return []
    
    # Validate price_order
    if price_order not in ['asc', 'desc']:
        raise ValueError("price_order must be either 'asc' or 'desc'")
    
    # Initialize database client
    try:
        db_client = SupabaseDB()
    except Exception as e:
        raise Exception(f"Failed to initialize database connection: {str(e)}")
    
    # Initialize filters if None
    if filters is None:
        filters = {}
    
    # Build the base query
    query = db_client.client.table('clothes_db').select('*')
    
    # Apply additional filters
    
    # Apply limit (increase limit for better filtering results)
    query = query.limit(max_items * 2000)  # Get more results for better filtering
    
    # Execute the query
    try:
        response = query.execute()
    except Exception as e:
        raise Exception(f"Database query failed: {str(e)}")
    
    # Extract and filter products
    products = []
    for item in response.data:
        # Extract numeric price for sorting
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
            'packshot_found': item.get('packshot_found')
        }
        
        # Calculate relevance score using new scoring system or fallback to old system
        if use_relevance_scoring:
            relevance_score = calculate_product_relevance_score(
                product=product,
                target_tags=search_terms,
                weights=scoring_weights
            )
            product['relevance_score'] = relevance_score
            
            # Include all products when using relevance scoring (let the score decide relevance)
            products.append(product)

    
    # Sort by relevance score and apply limit
    if use_relevance_scoring:
        # Primary sort: relevance score (descending), secondary sort: price (based on price_order)
        if sort_by_price:
            products.sort(key=lambda x: (-x['relevance_score'], x['price_numeric'] if price_order == 'asc' else -x['price_numeric']))
        else:
            # Sort only by relevance score (descending)
            products.sort(key=lambda x: x['relevance_score'], reverse=True)
    else:
        # Fallback to old sorting logic
        products.sort(key=lambda x: (x.get('search_score', 0), x['price_numeric']), reverse=True)
        
        # Sort by price if requested (after limiting results)
        if sort_by_price:
            products.sort(key=lambda x: x['price_numeric'], reverse=(price_order == 'desc'))
    
    # Apply final limit
    products = products[:max_items]
    
    return products
