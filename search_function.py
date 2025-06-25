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

def extract_material_building_blocks_dynamic(material_text: str) -> Set[str]:
    """
    Dynamically extract material building blocks from material text using regex patterns.
    This function identifies common material patterns and extracts individual components.
    
    Args:
        material_text (str): Material text like "55% lin, 45% bomull" or "100% linne"
    
    Returns:
        Set[str]: Set of individual material building blocks
    """
    if not material_text:
        return set()
    
    # Convert to lowercase for consistent processing
    material_lower = material_text.lower().strip()
    
    # Common material building blocks (base set)
    base_building_blocks = {
        'lin', 'linne', 'bomull', 'ull', 'siden', 'polyester', 'akryl', 'elastan', 
        'spandex', 'nylon', 'polyamid', 'viskos', 'rayon', 'modal', 'tencel', 
        'lyocell', 'kaschmir', 'kashmir', 'alpaca', 'merino', 'angora', 'mohair',
        'syntetisk', 'synthetic', 'blandat', 'mixed', 'recycled', 'återvunnen',
        'ekologisk', 'organic', 'bambu', 'bamboo', 'hampa', 'hemp', 'jute',
        'kokos', 'coconut', 'soja', 'soy', 'mikrofiber', 'microfiber', 'triacetat',
        'acetat', 'acetate', 'polyuretan', 'polyurethane', 'neopren', 'neoprene',
        'fleece', 'flanell', 'flannel', 'sammet', 'velvet', 'satin', 'siden',
        'silk', 'kaschmir', 'cashmere', 'merino', 'alpaca', 'angora', 'mohair'
    }
    
    found_materials = set()
    
    # Check for each building block in the material text
    for block in base_building_blocks:
        if block in material_lower:
            found_materials.add(block)
    
    # Use regex to find percentage patterns and extract materials
    # Pattern: "X% material" or "material X%"
    percentage_patterns = [
        r'(\d+(?:,\d+)?)\s*%\s*([a-zA-ZåäöÅÄÖ]+)',  # "55% lin"
        r'([a-zA-ZåäöÅÄÖ]+)\s*(\d+(?:,\d+)?)\s*%',  # "lin 55%"
    ]
    
    for pattern in percentage_patterns:
        matches = re.findall(pattern, material_lower)
        for match in matches:
            if len(match) == 2:
                # Extract the material part
                material_part = match[1] if match[0].replace(',', '').replace('.', '').isdigit() else match[0]
                # Clean up the material part
                material_part = re.sub(r'[^\wåäöÅÄÖ]', '', material_part).strip()
                if material_part and len(material_part) > 2:  # Minimum length check
                    found_materials.add(material_part)
    
    # Extract materials separated by commas, semicolons, or "och"/"and"
    separators = [',', ';', ' och ', ' and ', ' + ', '&']
    for separator in separators:
        if separator in material_lower:
            parts = material_lower.split(separator)
            for part in parts:
                part = part.strip()
                # Clean up the part and check if it's a valid material
                clean_part = re.sub(r'[^\wåäöÅÄÖ]', '', part).strip()
                if clean_part and len(clean_part) > 2:
                    # Check if it matches any known material pattern
                    for block in base_building_blocks:
                        if block in clean_part or clean_part in block:
                            found_materials.add(block)
                            break
    
    return found_materials

def extract_material_building_blocks(material_text: str) -> Set[str]:
    """
    Extract individual material building blocks from a material text.
    This is the legacy function that uses the static building blocks list.
    
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

def build_dynamic_material_building_blocks() -> Set[str]:
    """
    Dynamically build material building blocks from all materials in the database.
    This function analyzes all materials in the database and extracts unique building blocks.
    
    Returns:
        Set[str]: Set of all unique material building blocks found in the database
    """
    try:
        db_client = SupabaseDB()
        
        # Get all distinct materials from the database
        response = db_client.client.table('clothes_db').select('material').not_.is_('material', 'null').execute()
        
        if not response.data:
            return set()
        
        all_building_blocks = set()
        
        for item in response.data:
            material_raw = item.get('material')
            material = material_raw.strip() if material_raw is not None else ''
            if material:
                # Extract building blocks from this material using dynamic extraction
                building_blocks = extract_material_building_blocks_dynamic(material)
                all_building_blocks.update(building_blocks)
        
        return all_building_blocks
        
    except Exception as e:
        print(f"Error building dynamic material building blocks: {e}")
        return set()

def get_comprehensive_ai_data() -> Dict[str, Any]:
    """
    Get comprehensive data for AI decision-making including all clothing types, 
    materials, colors, and their combinations that exist in the database.
    
    Returns:
        Dict[str, Any]: Comprehensive data structure for AI decision-making
    """
    try:
        db_client = SupabaseDB()
        
        # Get all products from the database
        response = db_client.client.table('clothes_db').select('*').execute()
        
        if not response.data:
            return {
                'clothing_types': [],
                'materials': {'raw_materials': [], 'building_blocks': []},
                'colors': [],
                'combinations': {},
                'statistics': {
                    'total_products': 0,
                    'total_clothing_types': 0,
                    'total_materials': 0,
                    'total_colors': 0,
                    'total_combinations': 0
                }
            }
        
        # Initialize data structures
        clothing_types = set()
        raw_materials = set()
        all_building_blocks = set()
        colors = set()
        combinations = {}  # {clothing_type: {material: {color: count}}}
        
        # Process each product
        for product in response.data:
            clothing_type = product.get('clothing_type')
            material = product.get('material')
            color = product.get('dominant_tone')
            
            if clothing_type:
                clothing_types.add(clothing_type)
                
                # Initialize combination structure for this clothing type
                if clothing_type not in combinations:
                    combinations[clothing_type] = {}
                
                if material:
                    material = material.strip()
                    raw_materials.add(material)
                    
                    # Extract building blocks
                    building_blocks = extract_material_building_blocks_dynamic(material)
                    all_building_blocks.update(building_blocks)
                    
                    # Add to combinations
                    for block in building_blocks:
                        if block not in combinations[clothing_type]:
                            combinations[clothing_type][block] = {}
                        
                        if color:
                            colors.add(color)
                            if color not in combinations[clothing_type][block]:
                                combinations[clothing_type][block][color] = 0
                            combinations[clothing_type][block][color] += 1
            
            if color:
                colors.add(color)
        
        # Convert sets to sorted lists
        clothing_types_list = sorted(list(clothing_types))
        raw_materials_list = sorted(list(raw_materials))
        building_blocks_list = sorted(list(all_building_blocks))
        colors_list = sorted(list(colors))
        
        # Calculate statistics
        total_combinations = sum(
            len(color_dict) 
            for material_dict in combinations.values() 
            for color_dict in material_dict.values()
        )
        
        return {
            'clothing_types': clothing_types_list,
            'materials': {
                'raw_materials': raw_materials_list,
                'building_blocks': building_blocks_list
            },
            'colors': colors_list,
            'combinations': combinations,
            'statistics': {
                'total_products': len(response.data),
                'total_clothing_types': len(clothing_types_list),
                'total_materials': len(building_blocks_list),
                'total_colors': len(colors_list),
                'total_combinations': total_combinations
            }
        }
        
    except Exception as e:
        print(f"Error getting comprehensive AI data: {e}")
        return {
            'clothing_types': [],
            'materials': {'raw_materials': [], 'building_blocks': []},
            'colors': [],
            'combinations': {},
            'statistics': {
                'total_products': 0,
                'total_clothing_types': 0,
                'total_materials': 0,
                'total_colors': 0,
                'total_combinations': 0
            }
        }

def get_available_combinations_for_ai() -> Dict[str, List[Dict[str, str]]]:
    """
    Get all available combinations in a format optimized for AI decision-making.
    Returns a flat list of all valid combinations that exist in the database.
    
    Returns:
        Dict[str, List[Dict[str, str]]]: Dictionary with clothing_type as key and list of valid combinations as value
    """
    comprehensive_data = get_comprehensive_ai_data()
    combinations = comprehensive_data.get('combinations', {})
    
    ai_combinations = {}
    
    for clothing_type, material_dict in combinations.items():
        ai_combinations[clothing_type] = []
        
        for material, color_dict in material_dict.items():
            for color, count in color_dict.items():
                if count > 0:  # Only include combinations that actually exist
                    ai_combinations[clothing_type].append({
                        'clothing_type': clothing_type,
                        'material': material,
                        'color': color,
                        'product_count': count
                    })
    
    return ai_combinations

def get_material_color_availability_matrix() -> Dict[str, Dict[str, List[str]]]:
    """
    Get a matrix showing which materials are available in which colors for each clothing type.
    This provides a quick lookup for AI to understand material-color availability.
    
    Returns:
        Dict[str, Dict[str, List[str]]]: Matrix with clothing_type -> material -> available_colors
    """
    comprehensive_data = get_comprehensive_ai_data()
    combinations = comprehensive_data.get('combinations', {})
    
    matrix = {}
    
    for clothing_type, material_dict in combinations.items():
        matrix[clothing_type] = {}
        
        for material, color_dict in material_dict.items():
            available_colors = [color for color, count in color_dict.items() if count > 0]
            if available_colors:
                matrix[clothing_type][material] = sorted(available_colors)
    
    return matrix

def validate_combination_exists(clothing_type: str, material: str, color: str) -> Tuple[bool, int]:
    """
    Validate if a specific combination exists and return the product count.
    
    Args:
        clothing_type (str): The clothing type
        material (str): The material building block
        color (str): The color
    
    Returns:
        Tuple[bool, int]: (exists, product_count)
    """
    comprehensive_data = get_comprehensive_ai_data()
    combinations = comprehensive_data.get('combinations', {})
    
    if clothing_type in combinations:
        if material in combinations[clothing_type]:
            if color in combinations[clothing_type][material]:
                count = combinations[clothing_type][material][color]
                return True, count
    
    return False, 0

def get_best_available_combinations(clothing_type: str, preferred_materials: List[str] = None, 
                                  preferred_colors: List[str] = None, min_products: int = 1) -> List[Dict[str, Any]]:
    """
    Get the best available combinations for a clothing type, optionally filtered by preferences.
    
    Args:
        clothing_type (str): The clothing type to search for
        preferred_materials (List[str], optional): Preferred materials (will be prioritized)
        preferred_colors (List[str], optional): Preferred colors (will be prioritized)
        min_products (int, optional): Minimum number of products required for a combination
    
    Returns:
        List[Dict[str, Any]]: List of best combinations with metadata
    """
    comprehensive_data = get_comprehensive_ai_data()
    combinations = comprehensive_data.get('combinations', {})
    
    if clothing_type not in combinations:
        return []
    
    available_combinations = []
    
    for material, color_dict in combinations[clothing_type].items():
        for color, count in color_dict.items():
            if count >= min_products:
                # Calculate priority score
                priority_score = count  # Base score is product count
                
                # Boost priority for preferred materials
                if preferred_materials and material in preferred_materials:
                    priority_score *= 2
                
                # Boost priority for preferred colors
                if preferred_colors and color in preferred_colors:
                    priority_score *= 1.5
                
                available_combinations.append({
                    'clothing_type': clothing_type,
                    'material': material,
                    'color': color,
                    'product_count': count,
                    'priority_score': priority_score
                })
    
    # Sort by priority score (descending)
    available_combinations.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return available_combinations

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
        
        return {
            'raw_materials': raw_materials_list,
            'building_blocks': building_blocks_list
        }
        
    except Exception as e:
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

def calculate_product_relevance_score(product: Dict[str, Any], 
                                    target_material: Optional[str] = None,
                                    target_color: Optional[str] = None,
                                    search_terms: Optional[List[str]] = None,
                                    weights: Optional[Dict[str, float]] = None) -> float:
    """
    Calculate a comprehensive relevance score for a product based on material, color, and search term matches.
    
    Args:
        product (Dict[str, Any]): Product dictionary with all product information
        target_material (str, optional): Target material to match against
        target_color (str, optional): Target color to match against  
        search_terms (List[str], optional): List of search terms to match against
        weights (Dict[str, float], optional): Weights for different scoring components
                                            Default: {'material': 0.3, 'color': 0.3, 'search_terms': 0.4}
    
    Returns:
        float: Relevance score between 0 and 100 (higher is better)
    """
    # Default weights if not provided
    if weights is None:
        weights = {
            'material': 0.3,
            'color': 0.3, 
            'search_terms': 0.4
        }
    
    total_score = 0.0
    max_possible_score = 0.0
    
    # 1. Material Score (0-100 points)
    material_score = 0.0
    if target_material:
        max_possible_score += 100 * weights['material']
        product_material = product.get('material', '')
        
        if product_material:
            # Extract building blocks from both target and product materials
            target_blocks = extract_material_building_blocks_dynamic(target_material.lower())
            product_blocks = extract_material_building_blocks_dynamic(str(product_material).lower())
            
            if target_blocks and product_blocks:
                # Calculate intersection score
                intersection = target_blocks.intersection(product_blocks)
                union = target_blocks.union(product_blocks)
                
                if union:
                    # Jaccard similarity with bonus for exact matches
                    jaccard_score = len(intersection) / len(union)
                    material_score = jaccard_score * 100
                    
                    # Bonus for exact target material match
                    if target_material.lower() in product_material.lower():
                        material_score = min(100, material_score + 20)
                    
                    # Bonus for high overlap
                    if len(intersection) == len(target_blocks):
                        material_score = min(100, material_score + 10)
            
            # Fallback: simple substring matching
            elif target_material.lower() in product_material.lower():
                material_score = 80
        
        total_score += material_score * weights['material']
    
    # 2. Color Score (0-100 points)
    color_score = 0.0
    if target_color:
        max_possible_score += 100 * weights['color']
        product_color = product.get('dominant_tone', '').lower()
        target_color_lower = target_color.lower()
        
        if product_color:
            # Exact match
            if target_color_lower == product_color:
                color_score = 100
            # Partial match
            elif target_color_lower in product_color or product_color in target_color_lower:
                color_score = 80
            else:
                # Color similarity heuristics
                color_similarities = {
                    'blue': ['navy', 'teal', 'turquoise', 'azure'],
                    'red': ['burgundy', 'crimson', 'maroon', 'pink'],
                    'green': ['olive', 'forest', 'lime', 'mint'],
                    'black': ['charcoal', 'dark', 'navy'],
                    'white': ['cream', 'ivory', 'beige', 'off-white'],
                    'grey': ['gray', 'silver', 'charcoal'],
                    'brown': ['tan', 'beige', 'khaki', 'chocolate'],
                    'yellow': ['gold', 'amber', 'cream'],
                    'purple': ['violet', 'lavender', 'plum']
                }
                
                # Check for similar colors
                for base_color, similar_colors in color_similarities.items():
                    if target_color_lower == base_color and any(sim in product_color for sim in similar_colors):
                        color_score = 60
                        break
                    elif target_color_lower in similar_colors and base_color in product_color:
                        color_score = 60
                        break
        
        total_score += color_score * weights['color']
    
    # 3. Search Terms Score (0-100 points)
    search_terms_score = 0.0
    if search_terms:
        max_possible_score += 100 * weights['search_terms']
        
        # Combine all searchable text
        searchable_text = f"{product.get('name', '')} {product.get('description', '')} {product.get('material', '')}".lower()
        
        if searchable_text.strip():
            term_scores = []
            
            for term in search_terms:
                term_lower = term.lower().strip()
                if not term_lower:
                    continue
                
                term_score = 0
                
                # Exact word match in name (highest priority)
                name_lower = product.get('name', '').lower()
                if f" {term_lower} " in f" {name_lower} " or name_lower.startswith(term_lower) or name_lower.endswith(term_lower):
                    term_score += 40
                # Partial match in name
                elif term_lower in name_lower:
                    term_score += 25
                
                # Exact word match in description
                description_lower = product.get('description', '').lower()
                if f" {term_lower} " in f" {description_lower} " or description_lower.startswith(term_lower) or description_lower.endswith(term_lower):
                    term_score += 20
                # Partial match in description
                elif term_lower in description_lower:
                    term_score += 10
                
                # Match in material
                material_lower = product.get('material', '').lower()
                if term_lower in material_lower:
                    term_score += 15
                
                # Fuzzy matching for common fashion terms
                fashion_synonyms = {
                    'sweater': ['pullover', 'jumper', 'knitwear'],
                    'shirt': ['blouse', 'top'],
                    'pants': ['trousers', 'jeans'],
                    'dress': ['frock', 'gown'],
                    'jacket': ['blazer', 'coat'],
                    'crewneck': ['crew', 'round neck'],
                    'vneck': ['v-neck', 'v neck'],
                    'casual': ['relaxed', 'everyday'],
                    'formal': ['dressy', 'business']
                }
                
                # Check synonyms
                for base_term, synonyms in fashion_synonyms.items():
                    if term_lower == base_term:
                        for synonym in synonyms:
                            if synonym in searchable_text:
                                term_score += 10
                                break
                    elif term_lower in synonyms and base_term in searchable_text:
                        term_score += 10
                
                term_scores.append(min(100, term_score))
            
            # Average the scores, but give bonus for matching multiple terms
            if term_scores:
                avg_score = sum(term_scores) / len(term_scores)
                # Bonus for matching multiple terms
                multi_term_bonus = min(20, (len([s for s in term_scores if s > 0]) - 1) * 5)
                search_terms_score = min(100, avg_score + multi_term_bonus)
        
        total_score += search_terms_score * weights['search_terms']
    
    # Calculate final score (0-100 scale)
    if max_possible_score > 0:
        final_score = (total_score / max_possible_score) * 100
    else:
        final_score = 0
    
    # Add some debugging information to the score
    score_breakdown = {
        'total_score': final_score,
        'material_score': material_score,
        'color_score': color_score,
        'search_terms_score': search_terms_score,
        'weights_used': weights
    }
    
    return final_score

def search_database_products(clothing_type: str, filters: Optional[Dict] = None, 
                           max_items: int = 10, color: Optional[str] = None, 
                           sort_by_price: bool = False, price_order: str = 'asc',
                           search_terms: Optional[List[str]] = None,
                           use_relevance_scoring: bool = True,
                           scoring_weights: Optional[Dict[str, float]] = None) -> List[Dict]:
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
        use_relevance_scoring (bool, optional): Whether to use the new relevance scoring system. Defaults to True.
        scoring_weights (Dict[str, float], optional): Custom weights for scoring components.
        search_terms (List[str], optional): List of key terms to search for in name and description columns.
                                          This allows for more specific text-based searching.
        use_relevance_scoring (bool, optional): Whether to use the new relevance scoring system. Defaults to True.
        scoring_weights (Dict[str, float], optional): Custom weights for scoring components 
                                                    (material, color, search_terms). If None, uses defaults.
    
    Returns:
        list: List of dictionaries containing the products, sorted by relevance score or price.
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
    
    # Add color to filters if provided
    if color:
        # Use dominant_tone for color searching, case-insensitive
        filters['dominant_tone'] = color.lower()
    
    # Build the query
    query = db_client.client.table('clothes_db').select('*').eq('clothing_type', clothing_type)
    
    # Apply filters
    for key, value in filters.items():
        if value is None:
            continue
        elif key == 'material':
            # For material, search for materials containing the building block
            query = query.ilike('material', f'%{value.lower()}%')
        elif key == 'price_min':
            # Extract numeric price and filter
            query = query.gte('price_numeric', float(value))
        elif key == 'price_max':
            # Extract numeric price and filter
            query = query.lte('price_numeric', float(value))
        elif key == 'dominant_tone':
            # Case-insensitive color search on dominant_tone
            query = query.ilike('dominant_tone', f'%{value}%')
        else:
            # For other filters, use exact match
            query = query.eq(key, value)
    
    # Apply text search if search_terms are provided
    if search_terms and len(search_terms) > 0:
        # Create OR conditions for each search term across both name and description
        search_conditions = []
        for term in search_terms:
            term_lower = term.lower().strip()
            if term_lower:
                # Search in name column
                search_conditions.append(f"name.ilike.%{term_lower}%")
                # Search in description column
                search_conditions.append(f"description.ilike.%{term_lower}%")
        
        if search_conditions:
            # Apply the search conditions using OR logic
            # Note: Supabase doesn't support complex OR conditions directly in the query builder
            # So we'll need to handle this differently
            
            # For now, we'll apply the first search condition and filter results in Python
            # This is a limitation of the current Supabase query builder
            first_condition = search_conditions[0]
            if first_condition.startswith("name.ilike."):
                term = first_condition.replace("name.ilike.%", "").replace("%", "")
                query = query.or_(f"name.ilike.%{term}%,description.ilike.%{term}%")
            elif first_condition.startswith("description.ilike."):
                term = first_condition.replace("description.ilike.%", "").replace("%", "")
                query = query.or_(f"name.ilike.%{term}%,description.ilike.%{term}%")
    
    # Apply limit
    query = query.limit(max_items)
    
    # Execute the query
    try:
        response = query.execute()
    except Exception as e:
        raise Exception(f"Database query failed: {str(e)}")
    
    # Extract products from response
    products = []
    for item in response.data:
        # Extract numeric price for sorting
        price_numeric = extract_price(item.get('price', ''))
        
        product = {
            'id': item.get('id'),
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
        
        # Calculate relevance score if enabled
        if use_relevance_scoring:
            target_material = filters.get('material') if filters else None
            target_color = color
            
            relevance_score = calculate_product_relevance_score(
                product=product,
                target_material=target_material,
                target_color=target_color,
                search_terms=search_terms,
                weights=scoring_weights
            )
            product['relevance_score'] = relevance_score
        else:
            product['relevance_score'] = 0
        
        products.append(product)
    
    # Apply additional text search filtering if multiple search terms were provided
    if search_terms and len(search_terms) > 1:
        filtered_products = []
        for product in products:
            # Check if product matches any of the search terms
            product_text = f"{product.get('name', '')} {product.get('description', '')}".lower()
            matches_any_term = any(term.lower().strip() in product_text for term in search_terms if term.strip())
            if matches_any_term:
                filtered_products.append(product)
        products = filtered_products
    
    # Sort products based on scoring mode
    if use_relevance_scoring:
        # Primary sort: relevance score (descending), secondary sort: price (based on price_order)
        if sort_by_price:
            products.sort(key=lambda x: (-x['relevance_score'], x['price_numeric'] if price_order == 'asc' else -x['price_numeric']))
        else:
            # Sort only by relevance score (descending)
            products.sort(key=lambda x: x['relevance_score'], reverse=True)
    else:
        # Fallback to price-only sorting
        if sort_by_price:
            products.sort(key=lambda x: x['price_numeric'], reverse=(price_order == 'desc'))
    
    return products

def search_zalando_products(clothing_type, filters=None, max_items=10, color=None, sort_by_price=False, price_order='asc'):
    """
    Search products on Zalando website (fallback when database doesn't have enough results).
    
    Args:
        clothing_type (str): Type of clothing
        filters (dict, optional): Filters to apply
        max_items (int): Maximum number of items to return
        color (str, optional): Color filter
        sort_by_price (bool): Whether to sort by price
        price_order (str): Sort order ('asc' or 'desc')
    
    Returns:
        list: List of product dictionaries
    """
    # This is a placeholder for Zalando search functionality
    # In a real implementation, this would use the zalando_scraper module
    return []

def search_outfit(outfit_items, top_results_per_item=5, sort_by_price=False, price_order='asc', search_terms=None,
                  use_relevance_scoring=True, scoring_weights=None):
    """
    Search for a complete outfit based on a list of clothing items.
    
    Args:
        outfit_items (list): List of dictionaries, each containing:
            - clothing_type (str): Type of clothing
            - color (str, optional): Preferred color
            - filters (dict, optional): Additional filters
            - search_terms (list, optional): Key terms to search for in name and description
        top_results_per_item (int): Number of top results to return per item
        sort_by_price (bool): Whether to sort results by price
        price_order (str): Sort order ('asc' or 'desc')
                search_terms (List[str], optional): Global search terms to apply to all items
        use_relevance_scoring (bool, optional): Whether to use the new relevance scoring system. Defaults to True.
        scoring_weights (Dict[str, float], optional): Custom weights for scoring components.
        
    Returns:
        dict: Dictionary with clothing_type as key and list of products as value
    """
    results = {}
    
    for item in outfit_items:
        clothing_type = item.get('clothing_type')
        color = item.get('color')
        filters = item.get('filters', {})
        item_search_terms = item.get('search_terms', search_terms)  # Use item-specific or global search terms
        
        if clothing_type:
            try:
                products = search_database_products(
                    clothing_type=clothing_type,
                    filters=filters,
                    max_items=top_results_per_item,
                    color=color,
                    sort_by_price=sort_by_price,
                    price_order=price_order,
                    search_terms=item_search_terms,
                    use_relevance_scoring=use_relevance_scoring,
                    scoring_weights=scoring_weights
                )
                results[clothing_type] = products
            except Exception as e:
                results[clothing_type] = []
    
    return results

def get_database_stats():
    """Get basic statistics about the database"""
    try:
        db_client = SupabaseDB()
        response = db_client.client.table('clothes_db').select('*', count='exact').execute()
        return {'total_products': response.count}
    except Exception as e:
        return {'total_products': 0}

def get_available_clothing_types_from_database() -> List[str]:
    """
    Fetch all distinct clothing types from the database.
    
    Returns:
        List[str]: List of unique clothing types
    """
    try:
        db_client = SupabaseDB()
        
        # Get all distinct clothing types from the database
        response = db_client.client.table('clothes_db').select('clothing_type').not_.is_('clothing_type', 'null').execute()
        
        if not response.data:
            return []
        
        # Extract unique clothing types
        clothing_types = set()
        for item in response.data:
            clothing_type = item.get('clothing_type')
            if clothing_type:
                clothing_types.add(clothing_type)
        
        # Convert to sorted list
        clothing_types_list = sorted(list(clothing_types))
        
        return clothing_types_list
        
    except Exception as e:
        return []

def get_available_colors_from_database() -> List[str]:
    """
    Fetch all distinct colors from the database.
    
    Returns:
        List[str]: List of unique colors
    """
    try:
        db_client = SupabaseDB()
        
        # Get all distinct dominant tones from the database
        response = db_client.client.table('clothes_db').select('dominant_tone').not_.is_('dominant_tone', 'null').execute()
        
        if not response.data:
            return []
        
        # Extract unique colors
        colors = set()
        for item in response.data:
            color = item.get('dominant_tone')
            if color:
                colors.add(color)
        
        # Convert to sorted list
        colors_list = sorted(list(colors))
        
        return colors_list
        
    except Exception as e:
        return []

def get_database_inventory_summary() -> Dict[str, Any]:
    """
    Get a comprehensive summary of the database inventory.
    
    Returns:
        Dict[str, Any]: Summary containing clothing types, colors, and materials
    """
    try:
        # Get clothing types
        clothing_types = get_available_clothing_types_from_database()
        
        # Get colors
        colors = get_available_colors_from_database()
        
        # Get materials
        materials_data = get_available_materials_from_database()
        
        return {
            'clothing_types': clothing_types,
            'colors': colors,
            'materials': materials_data,
            'total_clothing_types': len(clothing_types),
            'total_colors': len(colors),
            'total_materials': len(materials_data.get('building_blocks', []))
        }
        
    except Exception as e:
        return {
            'clothing_types': [],
            'colors': [],
            'materials': {'raw_materials': [], 'building_blocks': []},
            'total_clothing_types': 0,
            'total_colors': 0,
            'total_materials': 0
        }

def get_detailed_inventory_by_clothing_type() -> Dict[str, Dict[str, Any]]:
    """
    Get detailed inventory analysis for each clothing type.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary with clothing_type as key and detailed data as value
    """
    try:
        db_client = SupabaseDB()
        
        # Get all products
        response = db_client.client.table('clothes_db').select('*').execute()
        
        if not response.data:
            return {}
        
        # Group products by clothing type
        products_by_type = {}
        for product in response.data:
            clothing_type = product.get('clothing_type')
            if not clothing_type:
                continue
                
            if clothing_type not in products_by_type:
                products_by_type[clothing_type] = []
            products_by_type[clothing_type].append(product)
        
        # Analyze each clothing type
        inventory_by_type = {}
        for clothing_type, products in products_by_type.items():
            # Extract unique materials
            materials = set()
            for product in products:
                material = product.get('material')
                if material:
                    # Extract building blocks from material
                    building_blocks = extract_material_building_blocks(material)
                    materials.update(building_blocks)
            
            # Extract unique colors
            colors = set()
            for product in products:
                color = product.get('dominant_tone')
                if color:
                    colors.add(color)
            
            # Create material-color combinations
            material_color_combinations = {}
            for product in products:
                material = product.get('material')
                color = product.get('dominant_tone')
                
                if material and color:
                    # Extract building blocks from material
                    building_blocks = extract_material_building_blocks(material)
                    
                    for block in building_blocks:
                        if block not in material_color_combinations:
                            material_color_combinations[block] = set()
                        material_color_combinations[block].add(color)
            
            # Convert sets to lists for JSON serialization
            inventory_by_type[clothing_type] = {
                'product_count': len(products),
                'materials': sorted(list(materials)),
                'colors': sorted(list(colors)),
                'material_color_combinations': {
                    material: sorted(list(colors)) 
                    for material, colors in material_color_combinations.items()
                }
            }
        
        return inventory_by_type
        
    except Exception as e:
        return {}

def get_available_combinations_for_clothing_type(clothing_type: str) -> Dict[str, Any]:
    """
    Get available material-color combinations for a specific clothing type.
    
    Args:
        clothing_type (str): The clothing type to analyze
    
    Returns:
        Dict[str, Any]: Dictionary containing available combinations
    """
    detailed_inventory = get_detailed_inventory_by_clothing_type()
    return detailed_inventory.get(clothing_type, {
        'product_count': 0,
        'materials': [],
        'colors': [],
        'material_color_combinations': {}
    })

def validate_material_color_combination(clothing_type: str, material: str, color: str) -> bool:
    """
    Validate if a material-color combination exists for a clothing type.
    
    Args:
        clothing_type (str): The clothing type
        material (str): The material building block
        color (str): The color
    
    Returns:
        bool: True if the combination exists, False otherwise
    """
    combinations = get_available_combinations_for_clothing_type(clothing_type)
    material_combinations = combinations.get('material_color_combinations', {})
    
    if material in material_combinations:
        return color in material_combinations[material]
    
    return False

# Test function for development
def test_database_search():
    """Test the database search functionality"""
    try:
        # Test database connection
        stats = get_database_stats()
        
        # Test material extraction
        materials = get_available_materials_from_database()
        
        # Test dynamic material building blocks
        dynamic_materials = build_dynamic_material_building_blocks()
        
        # Test comprehensive AI data
        comprehensive_data = get_comprehensive_ai_data()
        
        # Test material-color availability matrix
        availability_matrix = get_material_color_availability_matrix()
        
        # Test available combinations for AI
        ai_combinations = get_available_combinations_for_ai()
        
        # Test single product search
        results = search_database_products('sweaters', color='BLUE', max_items=5)
        
        # Test text search functionality
        text_search_results = search_products_by_text(['crewneck', 'sweater'], clothing_type='sweaters', max_items=5)
        
        # Test search with multiple terms
        multi_term_results = search_products_by_text(['lin', 'blue'], clothing_type='sweaters', max_items=5)
        
        # Test search with search_terms parameter in main search function
        search_terms_results = search_database_products('sweaters', search_terms=['crewneck'], max_items=5)
        
        # Test outfit search
        outfit_items = [
            {'clothing_type': 'sweaters', 'color': 'BLUE'},
            {'clothing_type': 'pants', 'color': 'BLACK'}
        ]
        outfit_results = search_outfit(outfit_items, top_results_per_item=3)
        
        # Test outfit search with text search
        outfit_items_with_text = [
            {'clothing_type': 'sweaters', 'color': 'BLUE', 'search_terms': ['crewneck']},
            {'clothing_type': 'pants', 'color': 'BLACK', 'search_terms': ['jeans']}
        ]
        outfit_text_results = search_outfit(outfit_items_with_text, top_results_per_item=3)
        
        # Test combination validation
        combination_exists, count = validate_combination_exists('sweaters', 'lin', 'BLUE')
        
        # Test best available combinations
        best_combinations = get_best_available_combinations('sweaters', preferred_materials=['lin'], min_products=1)
        
        # Test the new relevance scoring system
        scoring_test = test_relevance_scoring()
        
        return {
            'stats': stats,
            'materials': materials,
            'dynamic_materials': list(dynamic_materials),
            'comprehensive_data_summary': {
                'total_products': comprehensive_data.get('statistics', {}).get('total_products', 0),
                'total_clothing_types': comprehensive_data.get('statistics', {}).get('total_clothing_types', 0),
                'total_materials': comprehensive_data.get('statistics', {}).get('total_materials', 0),
                'total_colors': comprehensive_data.get('statistics', {}).get('total_colors', 0),
                'total_combinations': comprehensive_data.get('statistics', {}).get('total_combinations', 0)
            },
            'availability_matrix_sample': {k: v for k, v in list(availability_matrix.items())[:3]},
            'ai_combinations_sample': {k: v[:5] for k, v in list(ai_combinations.items())[:3]},
            'single_search': results,
            'text_search': {
                'crewneck_sweaters': text_search_results,
                'multi_term_search': multi_term_results,
                'search_terms_parameter': search_terms_results
            },
            'outfit_search': outfit_results,
            'outfit_search_with_text': outfit_text_results,
            'combination_validation': {
                'combination_exists': combination_exists,
                'product_count': count
            },
            'best_combinations_sample': best_combinations[:5],
            'relevance_scoring_test': scoring_test
        }
        
    except Exception as e:
        return {'error': str(e)}

def test_relevance_scoring():
    """Test the new relevance scoring functionality"""
    try:
        # Test with specific material and color requirements
        results_with_scoring = search_database_products(
            'sweaters', 
            filters={'material': 'lin'},
            color='BLUE',
            search_terms=['crewneck'],
            max_items=5,
            use_relevance_scoring=True
        )
        
        # Test without scoring (fallback)
        results_without_scoring = search_database_products(
            'sweaters', 
            filters={'material': 'lin'},
            color='BLUE',
            search_terms=['crewneck'],
            max_items=5,
            use_relevance_scoring=False,
            sort_by_price=True
        )
        
        # Test text search with scoring
        text_search_results = search_products_by_text(
            search_terms=['crewneck', 'sweater'],
            clothing_type='sweaters',
            max_items=5,
            use_relevance_scoring=True
        )
        
        # Test outfit search with scoring
        outfit_items = [
            {'clothing_type': 'sweaters', 'color': 'BLUE', 'search_terms': ['crewneck'], 'filters': {'material': 'lin'}},
            {'clothing_type': 'pants', 'color': 'BLACK', 'search_terms': ['jeans']}
        ]
        outfit_results = search_outfit(
            outfit_items, 
            top_results_per_item=3,
            use_relevance_scoring=True
        )
        
        return {
            'relevance_scoring_results': {
                'count': len(results_with_scoring),
                'top_scores': [
                    {
                        'name': p.get('name', 'Unknown'),
                        'relevance_score': p.get('relevance_score', 0),
                        'material': p.get('material', 'Unknown'),
                        'color': p.get('dominant_tone', 'Unknown')
                    } 
                    for p in results_with_scoring[:3]
                ]
            },
            'price_based_results': {
                'count': len(results_without_scoring),
                'products': [
                    {
                        'name': p.get('name', 'Unknown'),
                        'price': p.get('price', 'Unknown'),
                        'material': p.get('material', 'Unknown'),
                        'color': p.get('dominant_tone', 'Unknown')
                    } 
                    for p in results_without_scoring[:3]
                ]
            },
            'text_search_with_scoring': {
                'count': len(text_search_results),
                'top_scores': [
                    {
                        'name': p.get('name', 'Unknown'),
                        'relevance_score': p.get('relevance_score', 0)
                    }
                    for p in text_search_results[:3]
                ]
            },
            'outfit_search_scoring': {
                'clothing_types_found': list(outfit_results.keys()),
                'total_items': sum(len(products) for products in outfit_results.values())
            }
        }
        
    except Exception as e:
        return {'error': str(e)}

def get_ai_decision_support_data() -> Dict[str, Any]:
    """
    Get comprehensive data specifically formatted for AI decision-making.
    This provides all the granularity the AI needs to make good decisions.
    
    Returns:
        Dict[str, Any]: Comprehensive data structure optimized for AI decision-making
    """
    try:
        # Get comprehensive data
        comprehensive_data = get_comprehensive_ai_data()
        
        # Get availability matrix
        availability_matrix = get_material_color_availability_matrix()
        
        # Get all available combinations
        ai_combinations = get_available_combinations_for_ai()
        
        # Create a flat list of all valid combinations for easy AI processing
        all_valid_combinations = []
        for clothing_type, combinations in ai_combinations.items():
            for combo in combinations:
                all_valid_combinations.append({
                    'clothing_type': combo['clothing_type'],
                    'material': combo['material'],
                    'color': combo['color'],
                    'product_count': combo['product_count']
                })
        
        # Create material frequency data
        material_frequency = {}
        for clothing_type, combinations in ai_combinations.items():
            material_frequency[clothing_type] = {}
            for combo in combinations:
                material = combo['material']
                if material not in material_frequency[clothing_type]:
                    material_frequency[clothing_type][material] = 0
                material_frequency[clothing_type][material] += combo['product_count']
        
        # Create color frequency data
        color_frequency = {}
        for clothing_type, combinations in ai_combinations.items():
            color_frequency[clothing_type] = {}
            for combo in combinations:
                color = combo['color']
                if color not in color_frequency[clothing_type]:
                    color_frequency[clothing_type][color] = 0
                color_frequency[clothing_type][color] += combo['product_count']
        
        return {
            'statistics': comprehensive_data.get('statistics', {}),
            'clothing_types': comprehensive_data.get('clothing_types', []),
            'materials': comprehensive_data.get('materials', {}),
            'colors': comprehensive_data.get('colors', []),
            'availability_matrix': availability_matrix,
            'all_valid_combinations': all_valid_combinations,
            'material_frequency_by_clothing_type': material_frequency,
            'color_frequency_by_clothing_type': color_frequency,
            'combinations_by_clothing_type': ai_combinations,
            'examples': {
                'sample_combinations': all_valid_combinations[:10],
                'most_common_materials': sorted(
                    [(material, sum(freq.get(material, 0) for freq in material_frequency.values()))
                     for material in comprehensive_data.get('materials', {}).get('building_blocks', [])],
                    key=lambda x: x[1], reverse=True
                )[:10],
                'most_common_colors': sorted(
                    [(color, sum(freq.get(color, 0) for freq in color_frequency.values()))
                     for color in comprehensive_data.get('colors', [])],
                    key=lambda x: x[1], reverse=True
                )[:10]
            }
        }
        
    except Exception as e:
        print(f"Error getting AI decision support data: {e}")
        return {
            'statistics': {},
            'clothing_types': [],
            'materials': {},
            'colors': [],
            'availability_matrix': {},
            'all_valid_combinations': [],
            'material_frequency_by_clothing_type': {},
            'color_frequency_by_clothing_type': {},
            'combinations_by_clothing_type': {},
            'examples': {}
        }

def suggest_outfit_combinations(target_style: str = None, preferred_materials: List[str] = None, 
                              preferred_colors: List[str] = None, max_suggestions: int = 5) -> List[Dict[str, Any]]:
    """
    Suggest outfit combinations based on preferences and available inventory.
    
    Args:
        target_style (str, optional): Target style (e.g., 'casual', 'formal', 'business')
        preferred_materials (List[str], optional): Preferred materials
        preferred_colors (List[str], optional): Preferred colors
        max_suggestions (int): Maximum number of suggestions to return
    
    Returns:
        List[Dict[str, Any]]: List of suggested outfit combinations
    """
    try:
        # Get AI decision support data
        ai_data = get_ai_decision_support_data()
        
        # Get all valid combinations
        all_combinations = ai_data.get('all_valid_combinations', [])
        
        # Filter by preferences if provided
        filtered_combinations = all_combinations
        
        if preferred_materials:
            filtered_combinations = [
                combo for combo in filtered_combinations 
                if combo['material'] in preferred_materials
            ]
        
        if preferred_colors:
            filtered_combinations = [
                combo for combo in filtered_combinations 
                if combo['color'] in preferred_colors
            ]
        
        # Group by clothing type
        combinations_by_type = {}
        for combo in filtered_combinations:
            clothing_type = combo['clothing_type']
            if clothing_type not in combinations_by_type:
                combinations_by_type[clothing_type] = []
            combinations_by_type[clothing_type].append(combo)
        
        # Create outfit suggestions
        suggestions = []
        
        # Simple outfit combinations (top + bottom)
        top_types = ['sweaters', 't_shirts', 'shirts', 'blouses']
        bottom_types = ['pants', 'jeans', 'skirts', 'shorts']
        
        for top_type in top_types:
            if top_type not in combinations_by_type:
                continue
                
            for bottom_type in bottom_types:
                if bottom_type not in combinations_by_type:
                    continue
                
                # Get best combinations for each type
                top_combinations = sorted(
                    combinations_by_type[top_type], 
                    key=lambda x: x['product_count'], 
                    reverse=True
                )[:3]
                
                bottom_combinations = sorted(
                    combinations_by_type[bottom_type], 
                    key=lambda x: x['product_count'], 
                    reverse=True
                )[:3]
                
                # Create outfit suggestions
                for top_combo in top_combinations:
                    for bottom_combo in bottom_combinations:
                        # Calculate compatibility score
                        compatibility_score = 0
                        
                        # Boost score if colors are complementary
                        if top_combo['color'] != bottom_combo['color']:
                            compatibility_score += 1
                        
                        # Boost score if materials are compatible
                        if top_combo['material'] != bottom_combo['material']:
                            compatibility_score += 1
                        
                        # Boost score for higher product counts
                        compatibility_score += (top_combo['product_count'] + bottom_combo['product_count']) / 100
                        
                        suggestion = {
                            'outfit_type': f"{top_type} + {bottom_type}",
                            'top': top_combo,
                            'bottom': bottom_combo,
                            'compatibility_score': compatibility_score,
                            'total_products': top_combo['product_count'] + bottom_combo['product_count']
                        }
                        
                        suggestions.append(suggestion)
        
        # Sort by compatibility score and limit results
        suggestions.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        return suggestions[:max_suggestions]
        
    except Exception as e:
        print(f"Error suggesting outfit combinations: {e}")
        return []

def search_products_by_text(search_terms: List[str], clothing_type: Optional[str] = None, 
                           max_items: int = 20, filters: Optional[Dict] = None,
                           sort_by_price: bool = False, price_order: str = 'asc',
                           use_relevance_scoring: bool = True,
                           scoring_weights: Optional[Dict[str, float]] = None) -> List[Dict]:
    """
    Advanced text search function that searches across multiple text columns in the database.
    This function is designed for more specific and flexible text-based searching.
    
    Args:
        search_terms (List[str]): List of key terms to search for
        clothing_type (str, optional): Filter by specific clothing type
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
    
    # Apply clothing type filter if specified
    if clothing_type:
        if clothing_type not in CLOTHING_TYPES:
            raise ValueError(f"Invalid clothing type. Must be one of: {', '.join(CLOTHING_TYPES.keys())}")
        query = query.eq('clothing_type', clothing_type)
    
    # Apply additional filters
    for key, value in filters.items():
        if value is None:
            continue
        elif key == 'material':
            query = query.ilike('material', f'%{value.lower()}%')
        elif key == 'price_min':
            query = query.gte('price_numeric', float(value))
        elif key == 'price_max':
            query = query.lte('price_numeric', float(value))
        elif key == 'dominant_tone':
            query = query.ilike('dominant_tone', f'%{value}%')
        else:
            query = query.eq(key, value)
    
    # Apply text search using the first search term for database query
    # We'll do additional filtering in Python for multiple terms
    first_term = search_terms[0].lower().strip()
    if first_term:
        # Search in both name and description columns
        query = query.or_(f"name.ilike.%{first_term}%,description.ilike.%{first_term}%")
    
    # Apply limit (increase limit for better filtering results)
    query = query.limit(max_items * 2)  # Get more results for better filtering
    
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
            'id': item.get('id'),
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
            target_material = filters.get('material') if filters else None
            target_color = None  # Will be extracted from filters if present
            
            # Check if color is specified in filters
            for key, value in (filters or {}).items():
                if key == 'dominant_tone':
                    target_color = value
                    break
            
            relevance_score = calculate_product_relevance_score(
                product=product,
                target_material=target_material,
                target_color=target_color,
                search_terms=search_terms,
                weights=scoring_weights
            )
            product['relevance_score'] = relevance_score
            
            # Include all products when using relevance scoring (let the score decide relevance)
            products.append(product)
        else:
            # Fallback to old search scoring system
            search_score = 0
            product_text = f"{product.get('name', '')} {product.get('description', '')} {product.get('material', '')}".lower()
            
            for term in search_terms:
                term_lower = term.lower().strip()
                if term_lower:
                    # Check if term appears in product text
                    if term_lower in product_text:
                        search_score += 1
                        # Bonus points for exact matches in name
                        if term_lower in product.get('name', '').lower():
                            search_score += 2
                        # Bonus points for matches in description
                        if term_lower in product.get('description', '').lower():
                            search_score += 1
            
            # Only include products that match at least one search term
            if search_score > 0:
                product['search_score'] = search_score
                product['relevance_score'] = search_score * 10  # Convert to 0-100 scale approximately
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

if __name__ == "__main__":
    # Run test if executed directly
    test_results = test_database_search()
    if 'error' in test_results:
        pass
    else:
        pass
