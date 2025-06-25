#!/usr/bin/env python3
"""
Outfit Prompt Parser

This script parses natural language outfit descriptions into structured search parameters.
"""

import openai
import json
import os
import sys
from typing import List, Dict, Any, Optional

# Add the ai_server directory to the path to import search_function
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_server'))

from search_function import search_outfit, search_database_products, get_available_clothing_types_from_database, get_available_colors_from_database, get_available_materials_from_database

def parse_outfit_prompt(api_key: str, prompt: str) -> dict:
    """
    Parse a natural language outfit description into structured search parameters.
    
    Args:
        api_key (str): OpenAI API key
        prompt (str): Natural language description
        
    Returns:
        dict: Parsed outfit response
    """
    client = openai.OpenAI(api_key=api_key)
    
    # Dynamically fetch available options from the database
    clothing_types = get_available_clothing_types_from_database()
    colors = get_available_colors_from_database()
    materials_data = get_available_materials_from_database()
    materials = materials_data.get('building_blocks', [])

    # Get colors by clothing type for more accurate AI guidance
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_collection'))
    from supabase_db import SupabaseDB
    
    db_client = SupabaseDB()
    colors_by_type = {}
    
    for clothing_type in clothing_types:
        try:
            response = db_client.client.table('clothes_db').select('dominant_tone').eq('clothing_type', clothing_type).not_.is_('dominant_tone', 'null').execute()
            type_colors = list(set([item.get('dominant_tone') for item in response.data if item.get('dominant_tone')]))
            colors_by_type[clothing_type] = type_colors
        except:
            colors_by_type[clothing_type] = []

    system_prompt = f"""You are an expert fashion stylist. Parse the user's outfit description into structured search parameters.\n\n"""
    system_prompt += "Here are the available options in the database. Only use these values in your response.\n"
    system_prompt += f"Clothing types: {', '.join(clothing_types)}\n"
    system_prompt += f"Materials: {', '.join(materials)}\n\n"
    system_prompt += "Available colors by clothing type:\n"
    for clothing_type, type_colors in colors_by_type.items():
        system_prompt += f"  {clothing_type}: {', '.join(type_colors)}\n"
    system_prompt += "\n"
    system_prompt += "IMPORTANT: Only use colors that are available for each specific clothing type. If a requested color is not available for a clothing type, either:\n"
    system_prompt += "1. Choose a similar available color for that type, or\n"
    system_prompt += "2. Set color to null to search without color filter\n\n"
    system_prompt += "IMPORTANT: Do NOT put the color in the filters field. The color field is separate from filters.\n\n"
    system_prompt += "CRITICAL: The filters object should ONLY contain material, price_min, and price_max. NEVER include color in filters.\n\n"
    system_prompt += "Return a JSON object with this structure:\n"
    system_prompt += """{
    "outfit_description": "Description of the envisioned outfit",
    "outfit_items": [
        {
            "clothing_type": "(one of the available clothing types)",
            "color": "(one of the available colors for this type, or null)",
            "filters": {
                "material": "(one of the available materials, or null)",
                "price_min": null,
                "price_max": null
            }
        }
    ]
}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        
        # Handle markdown code blocks
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        content = content.strip()
        
        # Parse JSON
        parsed_response = json.loads(content)
        
        # Post-process: Remove color from filters if it exists
        outfit_items = parsed_response.get('outfit_items', [])
        for item in outfit_items:
            filters = item.get('filters', {})
            if 'dominant_tone' in filters:
                del filters['dominant_tone']
            if 'color' in filters:
                del filters['color']
        
        return parsed_response
        
    except Exception as e:
        return {'error': str(e)}

def search_outfit_from_prompt(api_key: str, prompt: str, top_results_per_item: int = 5, 
                              use_relevance_scoring: bool = True) -> Dict[str, Any]:
    """
    Search for an outfit based on a natural language prompt.
    
    Args:
        api_key (str): OpenAI API key
        prompt (str): Natural language outfit description
        top_results_per_item (int): Number of top results to return per item
        use_relevance_scoring (bool): Whether to use the new relevance scoring system
        
    Returns:
        Dict[str, Any]: Search results with parsed outfit and found products
    """
    # Parse the prompt
    outfit_response = parse_outfit_prompt(api_key, prompt)
    
    if 'error' in outfit_response:
        return outfit_response
    
    # Extract outfit items for search
    outfit_items = outfit_response.get('outfit_items', [])
    
    if not outfit_items:
        return {
            'error': 'No outfit items found in parsed response',
            'outfit_response': outfit_response
        }
    
    # Search for each item in the outfit
    try:
        search_results = search_outfit(
            outfit_items=outfit_items,
            top_results_per_item=top_results_per_item,
            sort_by_price=False,
            price_order='asc',
            use_relevance_scoring=use_relevance_scoring
        )
        
        return {
            'outfit_response': outfit_response,
            'search_results': search_results,
            'total_items_found': sum(len(products) for products in search_results.values())
        }
        
    except Exception as e:
        return {
            'error': f'Search failed: {str(e)}',
            'outfit_response': outfit_response,
            'search_results': {}
        }

def test_outfit_parser():
    """Test the outfit parser with actual database search"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {'error': 'OPENAI_API_KEY not set'}
    
    prompt = "casual summer outfit with blue shirts and white pants"
    
    try:
        results = search_outfit_from_prompt(api_key, prompt, top_results_per_item=3)
        return results
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    test_outfit_parser() 