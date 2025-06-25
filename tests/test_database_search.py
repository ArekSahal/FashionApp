#!/usr/bin/env python3
"""
Test script for database search functionality.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_collection'))

from search_function import (
    get_database_stats,
    get_database_inventory_summary,
    search_database_products,
    search_outfit,
    get_available_clothing_types_from_database,
    get_available_colors_from_database,
    get_available_materials_from_database
)
from outfit_prompt_parser import OutfitPromptParser

def test_database_connection():
    """Test database connection"""
    try:
        stats = get_database_stats()
        return stats['total_products'] > 0
    except Exception as e:
        return False

def test_inventory_extraction():
    """Test inventory extraction from database"""
    try:
        # Get clothing types, colors, and materials
        clothing_types = get_available_clothing_types_from_database()
        colors = get_available_colors_from_database()
        materials_data = get_available_materials_from_database()
        
        # Get inventory summary
        summary = get_database_inventory_summary()
        
        return (len(clothing_types) > 0 and 
                len(colors) > 0 and 
                len(materials_data.get('building_blocks', [])) > 0)
    except Exception as e:
        return False

def test_single_product_search():
    """Test single product search"""
    try:
        # Get available clothing types
        clothing_types = get_available_clothing_types_from_database()
        if not clothing_types:
            return False
        
        # Test search with first available clothing type
        test_clothing_type = clothing_types[0]
        colors = get_available_colors_from_database()
        test_color = colors[0] if colors else None
        
        results = search_database_products(
            clothing_type=test_clothing_type,
            color=test_color,
            max_items=3
        )
        
        return len(results) >= 0  # Just test that the function works
    except Exception as e:
        return False

def test_outfit_search():
    """Test outfit search functionality"""
    try:
        # Get available clothing types
        clothing_types = get_available_clothing_types_from_database()
        if len(clothing_types) < 2:
            return False
        
        # Create outfit items
        outfit_items = [
            {'clothing_type': clothing_types[0]},
            {'clothing_type': clothing_types[1]}
        ]
        
        # Search for outfit
        results = search_outfit(outfit_items, top_results_per_item=3)
        
        return len(results) > 0
    except Exception as e:
        return False

def test_ai_prompt_parsing():
    """Test AI prompt parsing"""
    try:
        # Check if API key is available
        if not os.getenv('OPENAI_API_KEY'):
            return False
        
        # Initialize parser
        parser = OutfitPromptParser(os.getenv('OPENAI_API_KEY'))
        
        # Test prompt parsing
        prompt = "casual summer outfit"
        outfit_response = parser.parse_outfit_prompt(prompt, max_items_per_category=1)
        
        return len(outfit_response['outfit_variations']) > 0
    except Exception as e:
        return False

def test_ai_outfit_search():
    """Test AI outfit search"""
    try:
        # Check if API key is available
        if not os.getenv('OPENAI_API_KEY'):
            return False
        
        # Initialize parser
        parser = OutfitPromptParser(os.getenv('OPENAI_API_KEY'))
        
        # Test outfit search
        prompt = "casual summer outfit"
        outfit_response = parser.parse_outfit_prompt(prompt, max_items_per_category=1)
        
        if not outfit_response['outfit_variations']:
            return False
        
        # Test searching for the first variation
        variation_name = outfit_response['outfit_variations'][0]['variation_name']
        results = parser.search_outfit_variation(variation_name, outfit_response)
        
        return True  # Just test that the function works
    except Exception as e:
        return False

def run_test_suite():
    """Run all tests"""
    tests = [
        ("Database Connection", test_database_connection),
        ("Inventory Extraction", test_inventory_extraction),
        ("Single Product Search", test_single_product_search),
        ("Outfit Search", test_outfit_search),
        ("AI Prompt Parsing", test_ai_prompt_parsing),
        ("AI Outfit Search", test_ai_outfit_search)
    ]
    
    passed = 0
    total = len(tests)
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "PASSED" if result else "FAILED"
            if result:
                passed += 1
        except Exception as e:
            results[test_name] = f"ERROR: {e}"
    
    return passed, total, results

def main():
    """Main test function"""
    # Check if Supabase key is set
    if not os.getenv('SUPABASE_KEY'):
        return
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        return
    
    # Run tests
    passed, total, results = run_test_suite()
    
    # Return results (no printing)
    return {
        'passed': passed,
        'total': total,
        'results': results
    }

if __name__ == "__main__":
    main() 