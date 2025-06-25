# create a function that takes a number of parameters and searches the Supabase database with filters
#  example of how it would be used:
# I want a blue crewneck sweater 
# Then the function would take filters as inputs such as color blue and type of clothing is sweater
# the function would then return the products matching the filters

# the function would use the supabase_db.py file to search the database with the filters
# the function would return the products

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_collection'))

from supabase_db import SupabaseDB
from zalando_scraper import (
    CLOTHING_TYPES, 
    COLORS, 
    MATERIALS,
    validate_material
)
import re
from tqdm import tqdm
from typing import List, Dict, Optional, Any, Set

def extract_material_building_blocks(material_text: str) -> Set[str]:
    """
    Extract individual material building blocks from a material text.
    
    Args:
        material_text (str): Material text like "55% lin, 45% bomull" or "100% linne"
    
    Returns:
        Set[str]: Set of individual material building blocks
    """
    if not material_text:
        return set()
    
    # Convert to lowercase for consistent processing
    material_lower = material_text.lower().strip()
    
    # Common material building blocks
    building_blocks = {
        'lin', 'linne', 'bomull', 'ull', 'siden', 'polyester', 'akryl', 'elastan', 
        'spandex', 'nylon', 'polyamid', 'viskos', 'rayon', 'modal', 'tencel', 
        'lyocell', 'kaschmir', 'kashmir', 'alpaca', 'merino', 'angora', 'mohair',
        'syntetisk', 'synthetic', 'blandat', 'mixed', 'recycled', 'återvunnen',
        'ekologisk', 'organic', 'bambu', 'bamboo', 'hampa', 'hemp', 'jute',
        'kokos', 'coconut', 'soja', 'soy', 'mikrofiber', 'microfiber'
    }
    
    found_materials = set()
    
    # Check for each building block in the material text
    for block in building_blocks:
        if block in material_lower:
            found_materials.add(block)
    
    return found_materials

def get_available_materials_from_database() -> Dict[str, List[str]]:
    """
    Fetch all distinct materials from the database and extract building blocks.
    
    Returns:
        Dict[str, List[str]]: Dictionary with 'raw_materials' and 'building_blocks' lists
    """
    try:
        db_client = SupabaseDB()
        
        # Get all distinct materials from the database
        response = db_client.client.table('clothes_db').select('material').not_.is_('material', 'null').execute()
        
        if not response.data:
            print("⚠️ No materials found in database")
            return {'raw_materials': [], 'building_blocks': []}
        
        # Extract unique materials
        raw_materials = set()
        all_building_blocks = set()
        
        for item in response.data:
            material_raw = item.get('material')
            material = material_raw.strip() if material_raw is not None else ''
            if material:
                raw_materials.add(material)
                
                # Extract building blocks from this material
                building_blocks = extract_material_building_blocks(material)
                all_building_blocks.update(building_blocks)
        
        # Convert to sorted lists
        raw_materials_list = sorted(list(raw_materials))
        building_blocks_list = sorted(list(all_building_blocks))
        
        print(f"📊 Found {len(raw_materials_list)} unique materials in database")
        print(f"🔧 Extracted {len(building_blocks_list)} material building blocks")
        
        return {
            'raw_materials': raw_materials_list,
            'building_blocks': building_blocks_list
        }
        
    except Exception as e:
        print(f"❌ Error fetching materials from database: {e}")
        return {'raw_materials': [], 'building_blocks': []}

def search_materials_in_database(material_query: str) -> List[str]:
    """
    Search for materials in the database that contain the given query.
    
    Args:
        material_query (str): Material to search for (e.g., 'lin', 'bomull')
    
    Returns:
        List[str]: List of matching material strings from the database
    """
    try:
        db_client = SupabaseDB()
        
        # Search for materials containing the query (case insensitive)
        response = db_client.client.table('clothes_db').select('material').ilike('material', f'%{material_query.lower()}%').execute()
        
        if not response.data:
            return []
        
        # Extract unique matching materials
        matching_materials = set()
        for item in response.data:
            material_raw = item.get('material')
            material = material_raw.strip() if material_raw is not None else ''
            if material:
                matching_materials.add(material)
        
        return sorted(list(matching_materials))
        
    except Exception as e:
        print(f"❌ Error searching materials in database: {e}")
        return []

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

def search_database_products(clothing_type: str, filters: Optional[Dict] = None, 
                           max_items: int = 10, color: Optional[str] = None, 
                           sort_by_price: bool = False, price_order: str = 'asc') -> List[Dict]:
    """
    Search products in the Supabase database with filters.
    
    Args:
        clothing_type (str): Type of clothing (e.g., 'sweaters', 't_shirts', 'shirts')
        filters (dict, optional): Dictionary of filters to apply (e.g., {'material': 'linne', 'size': 'M'})
        max_items (int, optional): Maximum number of products to return. Defaults to 10.
        color (str, optional): Color of the item (e.g., 'BLUE', 'BLACK', 'RED'). 
                             This is a convenience parameter that will be added to filters.
        sort_by_price (bool, optional): Whether to sort results by price. Defaults to False.
        price_order (str, optional): Sort order for price ('asc' or 'desc'). Defaults to 'asc'.
    
    Returns:
        list: List of dictionaries containing the products, optionally sorted by price.
    """
    # Validate clothing type
    if clothing_type not in CLOTHING_TYPES:
        raise ValueError(f"Invalid clothing type. Must be one of: {', '.join(CLOTHING_TYPES.keys())}")
    
    # Explicitly reject shoes
    if clothing_type == 'shoes':
        raise ValueError("Shoes are not supported in this search system")
    
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
    
    # Add color to filters if provided (convenience parameter)
    if color:
        filters['color'] = color.upper()
    
    tqdm.write(f"\n🔍 Searching database for {clothing_type} products...")
    
    try:
        # Start with base query for clothing type
        query = db_client.client.table('clothes_db').select('*').eq('clothing_type', clothing_type)
        
        # Apply color filter if specified
        if 'color' in filters and filters['color']:
            # Map color names to database color fields
            color_mapping = {
                'BLUE': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'BLACK': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'WHITE': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'RED': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'GREEN': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'BROWN': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'GRAY': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'BEIGE': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'OLIVE': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'NAVY': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'PINK': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'YELLOW': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'PURPLE': ['dominant_tone', 'dominant_hue', 'dominant_shade'],
                'ORANGE': ['dominant_tone', 'dominant_hue', 'dominant_shade']
            }
            
            target_color = filters['color']
            if target_color in color_mapping:
                # Create OR condition for color fields
                color_conditions = []
                for color_field in color_mapping[target_color]:
                    color_conditions.append(f"{color_field}.ilike.%{target_color.lower()}%")
                
                # Apply color filter using OR logic
                query = query.or_(','.join(color_conditions))
        
        # Apply material filter if specified - now with improved partial matching
        if 'material' in filters and filters['material']:
            material = filters['material'].lower()
            # Search for the material in the material field (partial match)
            query = query.ilike('material', f'%{material}%')
            tqdm.write(f"🔧 Searching for materials containing: {material}")
        
        if 'upper_material' in filters and filters['upper_material']:
            material = filters['upper_material'].lower()
            # Search for the material in the material field (partial match)
            query = query.ilike('material', f'%{material}%')
            tqdm.write(f"🔧 Searching for upper materials containing: {material}")
        
        # Apply q parameter (specific clothing types) if specified
        if 'q' in filters and filters['q']:
            q_value = filters['q'].lower()
            # Search in name and description
            query = query.or_(f"name.ilike.%{q_value}%,description.ilike.%{q_value}%")
        
        # Get more items than requested to account for filtering
        fetch_limit = max_items * 3  # Get 3x more to account for filtering
        query = query.limit(fetch_limit)
        
        # Execute query
        response = query.execute()
        
        if not response.data:
            tqdm.write(f"❌ No {clothing_type} products found in database")
            return []
        
        products = response.data
        tqdm.write(f"📊 Found {len(products)} {clothing_type} products in database")
        
        # Apply additional client-side filtering
        filtered_products = []
        for product in products:
            # Add price value for sorting
            product['price_value'] = extract_price(product.get('price', ''))
            
            # Additional filtering logic can be added here
            # For now, we'll include all products and let sorting handle the rest
            filtered_products.append(product)
        
        # Sort products if requested
        if sort_by_price:
            tqdm.write(f"\n💰 Sorting products by price ({price_order})...")
            filtered_products.sort(key=lambda x: x['price_value'] if price_order == 'asc' else -x['price_value'])
        
        # Return top results
        top_products = filtered_products[:max_items]
        tqdm.write(f"✅ Returning top {len(top_products)} {clothing_type} products")
        
        return top_products
        
    except Exception as e:
        tqdm.write(f"❌ Error searching database: {str(e)}")
        return []

def search_zalando_products(clothing_type, filters=None, max_items=10, color=None, sort_by_price=False, price_order='asc'):
    """
    Search products in the Supabase database with filters.
    This is a wrapper function that maintains compatibility with existing code.
    
    Args:
        clothing_type (str): Type of clothing (e.g., 'sweaters', 't_shirts', 'shirts')
        filters (dict, optional): Dictionary of filters to apply (e.g., {'color': 'BLUE', 'size': 'M'})
        max_items (int, optional): Maximum number of products to return. Defaults to 10.
        color (str, optional): Color of the item (e.g., 'BLUE', 'BLACK', 'RED'). 
                             This is a convenience parameter that will be added to filters.
        sort_by_price (bool, optional): Whether to sort results by price. Defaults to False.
        price_order (str, optional): Sort order for price ('asc' or 'desc'). Defaults to 'asc'.
    
    Returns:
        list: List of dictionaries containing the products, optionally sorted by price.
    """
    return search_database_products(
        clothing_type=clothing_type,
        filters=filters,
        max_items=max_items,
        color=color,
        sort_by_price=sort_by_price,
        price_order=price_order
    )

def search_outfit(outfit_items, top_results_per_item=5, sort_by_price=False, price_order='asc'):
    """
    Search for multiple clothing items to create an outfit from the database.
    
    Args:
        outfit_items (list): List of dictionaries, each containing search parameters for an item.
                            Each dictionary should have:
                            - clothing_type (str): Type of clothing (e.g., 'sweaters', 't_shirts')
                            - filters (dict, optional): Filters to apply
                            - color (str, optional): Color of the item
                            - max_items (int, optional): Max items to search (defaults to 100)
        top_results_per_item (int, optional): Number of top results to return per item. Defaults to 5.
        sort_by_price (bool, optional): Whether to sort results by price. Defaults to False.
        price_order (str, optional): Sort order for price ('asc' or 'desc'). Defaults to 'asc'.
    
    Returns:
        dict: Dictionary with clothing types as keys and lists of top products as values.
              Example: {'sweaters': [product1, product2, ...], 'pants': [product1, product2, ...]}
    """
    outfit_results = {}
    
    tqdm.write(f"\n👕 Searching database for outfit with {len(outfit_items)} items...")
    
    for i, item in enumerate(outfit_items, 1):
        tqdm.write(f"\n--- Searching for item {i}/{len(outfit_items)}: {item.get('clothing_type', 'Unknown')} ---")
        
        # Extract parameters from item dictionary
        clothing_type = item.get('clothing_type')
        filters = item.get('filters', {})
        color = item.get('color')
        max_items = item.get('max_items', 100)
        
        if not clothing_type:
            tqdm.write(f"⚠️ Warning: Item {i} missing 'clothing_type', skipping...")
            continue
        
        # Skip shoes - they are not supported
        if clothing_type == 'shoes':
            tqdm.write(f"⚠️ Warning: Shoes are not supported, skipping item {i}...")
            continue
        
        try:
            # Search for this item in the database
            products = search_database_products(
                clothing_type=clothing_type,
                filters=filters,
                max_items=max_items,
                color=color,
                sort_by_price=sort_by_price,
                price_order=price_order
            )
            
            # Take top results for this item
            top_products = products[:top_results_per_item]
            outfit_results[clothing_type] = top_products
            
            tqdm.write(f"✅ Found {len(products)} products, returning top {len(top_products)} for {clothing_type}")
            
        except Exception as e:
            tqdm.write(f"❌ Error searching for {clothing_type}: {str(e)}")
            outfit_results[clothing_type] = []
    
    tqdm.write(f"\n🎉 Outfit search complete! Found results for {len(outfit_results)} item types.")
    return outfit_results

def get_database_stats():
    """
    Get statistics about the database.
    
    Returns:
        dict: Database statistics
    """
    try:
        db_client = SupabaseDB()
        return db_client.get_database_stats()
    except Exception as e:
        return {'error': f"Failed to get database stats: {str(e)}"}

def get_available_clothing_types_from_database() -> List[str]:
    """
    Fetch all distinct clothing types from the database.
    
    Returns:
        List[str]: List of available clothing types
    """
    try:
        db_client = SupabaseDB()
        
        # Get all distinct clothing types from the database
        response = db_client.client.table('clothes_db').select('clothing_type').not_.is_('clothing_type', 'null').execute()
        
        if not response.data:
            print("⚠️ No clothing types found in database")
            return []
        
        # Extract unique clothing types
        clothing_types = set()
        for item in response.data:
            clothing_type_raw = item.get('clothing_type')
            clothing_type = clothing_type_raw.strip() if clothing_type_raw is not None else ''
            if clothing_type:
                clothing_types.add(clothing_type)
        
        # Convert to sorted list
        clothing_types_list = sorted(list(clothing_types))
        
        print(f"👕 Found {len(clothing_types_list)} unique clothing types in database")
        
        return clothing_types_list
        
    except Exception as e:
        print(f"❌ Error fetching clothing types from database: {e}")
        return []

def get_available_colors_from_database() -> List[str]:
    """
    Fetch all distinct colors from the database by analyzing color fields.
    
    Returns:
        List[str]: List of available colors
    """
    try:
        db_client = SupabaseDB()
        
        # Get all products with color information
        response = db_client.client.table('clothes_db').select('dominant_tone,dominant_hue,dominant_shade,overall_tone,overall_hue,overall_shade').not_.is_('dominant_tone', 'null').execute()
        
        if not response.data:
            print("⚠️ No color data found in database")
            return []
        
        # Extract unique colors from all color fields
        colors = set()
        for item in response.data:
            # Check all color fields
            color_fields = ['dominant_tone', 'dominant_hue', 'dominant_shade', 'overall_tone', 'overall_hue', 'overall_shade']
            for field in color_fields:
                color_raw = item.get(field)
                color = color_raw.strip() if color_raw is not None else ''
                if color and color.lower() not in ['', 'none', 'null', 'undefined']:
                    # Convert to uppercase for consistency
                    colors.add(color.upper())
        
        # Convert to sorted list
        colors_list = sorted(list(colors))
        
        print(f"🎨 Found {len(colors_list)} unique colors in database")
        
        return colors_list
        
    except Exception as e:
        print(f"❌ Error fetching colors from database: {e}")
        return []

def get_database_inventory_summary() -> Dict[str, Any]:
    """
    Get a comprehensive summary of available inventory in the database.
    
    Returns:
        Dict[str, Any]: Summary containing clothing types, colors, and materials
    """
    try:
        # Get all the data
        clothing_types = get_available_clothing_types_from_database()
        colors = get_available_colors_from_database()
        materials_data = get_available_materials_from_database()
        
        summary = {
            'clothing_types': clothing_types,
            'colors': colors,
            'materials': materials_data.get('building_blocks', []),
            'raw_materials': materials_data.get('raw_materials', []),
            'total_clothing_types': len(clothing_types),
            'total_colors': len(colors),
            'total_materials': len(materials_data.get('building_blocks', [])),
            'total_raw_materials': len(materials_data.get('raw_materials', []))
        }
        
        print(f"📊 Database Inventory Summary:")
        print(f"   👕 Clothing Types: {len(clothing_types)}")
        print(f"   🎨 Colors: {len(colors)}")
        print(f"   🔧 Material Building Blocks: {len(materials_data.get('building_blocks', []))}")
        print(f"   📝 Raw Materials: {len(materials_data.get('raw_materials', []))}")
        
        return summary
        
    except Exception as e:
        print(f"❌ Error getting database inventory summary: {e}")
        return {
            'clothing_types': [],
            'colors': [],
            'materials': [],
            'raw_materials': [],
            'total_clothing_types': 0,
            'total_colors': 0,
            'total_materials': 0,
            'total_raw_materials': 0
        }

def get_detailed_inventory_by_clothing_type() -> Dict[str, Dict[str, Any]]:
    """
    Get detailed inventory information showing which materials and colors are available for each clothing type.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary with clothing types as keys and detailed inventory info as values
        Example:
        {
            "shirts": {
                "materials": ["lin", "bomull", "polyester"],
                "colors": ["BLUE", "WHITE", "BLACK"],
                "material_color_combinations": {
                    "lin": ["BLUE", "WHITE", "BEIGE"],
                    "bomull": ["WHITE", "BLACK", "BLUE"],
                    "polyester": ["BLACK", "GRAY"]
                },
                "product_count": 45
            }
        }
    """
    try:
        db_client = SupabaseDB()
        
        # Get all products with their details
        response = db_client.client.table('clothes_db').select(
            'clothing_type,material,dominant_tone,dominant_hue,dominant_shade,overall_tone,overall_hue,overall_shade'
        ).not_.is_('clothing_type', 'null').execute()
        
        if not response.data:
            print("⚠️ No products found in database")
            return {}
        
        # Organize data by clothing type
        inventory_by_type = {}
        
        for item in response.data:
            clothing_type = item.get('clothing_type')
            if clothing_type is None:
                continue
            clothing_type = clothing_type.strip()
            if not clothing_type:
                continue
            
            # Initialize clothing type entry if not exists
            if clothing_type not in inventory_by_type:
                inventory_by_type[clothing_type] = {
                    'materials': set(),
                    'colors': set(),
                    'material_color_combinations': {},
                    'product_count': 0
                }
            
            # Count product
            inventory_by_type[clothing_type]['product_count'] += 1
            
            # Extract materials
            material_raw = item.get('material')
            material = material_raw.strip() if material_raw is not None else ''
            if material:
                # Extract building blocks from material
                building_blocks = extract_material_building_blocks(material)
                inventory_by_type[clothing_type]['materials'].update(building_blocks)
                
                # Track material-color combinations
                for block in building_blocks:
                    if block not in inventory_by_type[clothing_type]['material_color_combinations']:
                        inventory_by_type[clothing_type]['material_color_combinations'][block] = set()
            
            # Extract colors from all color fields
            color_fields = ['dominant_tone', 'dominant_hue', 'dominant_shade', 'overall_tone', 'overall_hue', 'overall_shade']
            item_colors = set()
            
            for field in color_fields:
                color_raw = item.get(field)
                color = color_raw.strip() if color_raw is not None else ''
                if color and color.lower() not in ['', 'none', 'null', 'undefined']:
                    item_colors.add(color.upper())
            
            # Add colors to overall color set
            inventory_by_type[clothing_type]['colors'].update(item_colors)
            
            # Add colors to material-color combinations
            if material and item_colors:
                building_blocks = extract_material_building_blocks(material)
                for block in building_blocks:
                    if block in inventory_by_type[clothing_type]['material_color_combinations']:
                        inventory_by_type[clothing_type]['material_color_combinations'][block].update(item_colors)
        
        # Convert sets to sorted lists for better readability
        for clothing_type, data in inventory_by_type.items():
            data['materials'] = sorted(list(data['materials']))
            data['colors'] = sorted(list(data['colors']))
            
            # Convert material-color combinations to sorted lists
            for material, colors in data['material_color_combinations'].items():
                data['material_color_combinations'][material] = sorted(list(colors))
        
        print(f"📊 Detailed inventory analysis complete:")
        print(f"   👕 Analyzed {len(inventory_by_type)} clothing types")
        for clothing_type, data in inventory_by_type.items():
            print(f"   {clothing_type}: {data['product_count']} products, {len(data['materials'])} materials, {len(data['colors'])} colors")
        
        return inventory_by_type
        
    except Exception as e:
        print(f"❌ Error getting detailed inventory by clothing type: {e}")
        return {}

def get_available_combinations_for_clothing_type(clothing_type: str) -> Dict[str, Any]:
    """
    Get available materials and colors for a specific clothing type.
    
    Args:
        clothing_type (str): The clothing type to get combinations for
    
    Returns:
        Dict[str, Any]: Available materials, colors, and combinations for the clothing type
    """
    detailed_inventory = get_detailed_inventory_by_clothing_type()
    
    if clothing_type not in detailed_inventory:
        return {
            'materials': [],
            'colors': [],
            'material_color_combinations': {},
            'product_count': 0
        }
    
    return detailed_inventory[clothing_type]

def validate_material_color_combination(clothing_type: str, material: str, color: str) -> bool:
    """
    Validate if a material-color combination exists for a specific clothing type.
    
    Args:
        clothing_type (str): The clothing type
        material (str): The material building block
        color (str): The color
    
    Returns:
        bool: True if the combination exists, False otherwise
    """
    detailed_inventory = get_detailed_inventory_by_clothing_type()
    
    if clothing_type not in detailed_inventory:
        return False
    
    clothing_data = detailed_inventory[clothing_type]
    
    # Check if material exists for this clothing type
    if material not in clothing_data['materials']:
        return False
    
    # Check if color exists for this clothing type
    if color not in clothing_data['colors']:
        return False
    
    # Check if the specific combination exists
    material_combinations = clothing_data['material_color_combinations']
    if material in material_combinations and color in material_combinations[material]:
        return True
    
    return False

# Example usage:
if __name__ == "__main__":
    # Example 1: Search for blue sweaters from database
    print("🔍 Testing database search...")
    
    try:
        # Get database stats first
        stats = get_database_stats()
        print(f"📊 Database stats: {stats}")
        
        # Get available materials
        materials = get_available_materials_from_database()
        print(f"🔧 Available material building blocks: {materials['building_blocks']}")
        
        # Search for blue sweaters
        results = search_database_products(
            clothing_type='sweaters',
            color='BLUE',
            max_items=5,
            sort_by_price=True
        )
        
        print(f"\nFound {len(results)} blue sweaters")
        for i, product in enumerate(results, 1):
            print(f"{i}. {product['name']} - {product['price']}")
        
        # Example 2: Search for an outfit
        outfit_items = [
            {
                'clothing_type': 'sweaters',
                'color': 'BLUE',
                'max_items': 5
            },
            {
                'clothing_type': 'pants',
                'color': 'BLACK',
                'max_items': 5
            }
        ]
        
        outfit_results = search_outfit(outfit_items, top_results_per_item=3)
        
        print("\n👕 Outfit search results:")
        for clothing_type, products in outfit_results.items():
            print(f"\n{clothing_type}:")
            for i, product in enumerate(products, 1):
                print(f"  {i}. {product['name']} - {product['price']}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure SUPABASE_KEY environment variable is set!")
