#!/usr/bin/env python3
"""
Simple test script for outfit search functionality.
"""

import os
import sys
import json

# Add the ai_server directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_server'))

from search_function import search_database_products, get_database_stats, get_available_clothing_types_from_database, get_available_colors_from_database, get_available_materials_from_database
from outfit_prompt_parser import search_outfit_from_prompt

def test_database_connection():
    """Test if we can connect to the database"""
    print("🔍 Testing database connection...")
    try:
        stats = get_database_stats()
        print(f"✅ Database connected! Total products: {stats.get('total_products', 0)}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_available_clothing_types():
    """Test what clothing types are available"""
    print("\n👕 Testing available clothing types...")
    try:
        clothing_types = get_available_clothing_types_from_database()
        print(f"✅ Available clothing types: {clothing_types}")
        return clothing_types
    except Exception as e:
        print(f"❌ Failed to get clothing types: {e}")
        return []

def test_available_colors():
    """Test what colors are available"""
    print("\n🎨 Testing available colors...")
    try:
        colors = get_available_colors_from_database()
        print(f"✅ Available colors: {colors[:10]}...")  # Show first 10 colors
        return colors
    except Exception as e:
        print(f"❌ Failed to get colors: {e}")
        return []

def test_dominant_hue_field():
    """Test what's actually in the dominant_hue field"""
    print("\n🎨 Testing dominant_hue field...")
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'data_collection'))
        from supabase_db import SupabaseDB
        
        db_client = SupabaseDB()
        response = db_client.client.table('clothes_db').select('dominant_hue').not_.is_('dominant_hue', 'null').limit(10).execute()
        
        if response.data:
            hues = [item.get('dominant_hue') for item in response.data if item.get('dominant_hue')]
            print(f"✅ Sample dominant_hue values: {hues}")
            return hues
        else:
            print("❌ No dominant_hue values found")
            return []
    except Exception as e:
        print(f"❌ Failed to get dominant_hue: {e}")
        return []

def test_simple_search():
    """Test a simple search"""
    print("\n🔍 Testing simple search...")
    try:
        # Get available clothing types
        clothing_types = get_available_clothing_types_from_database()
        if not clothing_types:
            print("❌ No clothing types available")
            return False
        
        # Test search with first available type
        test_type = clothing_types[0]
        print(f"🔍 Searching for {test_type}...")
        
        results = search_database_products(
            clothing_type=test_type,
            max_items=3
        )
        
        print(f"✅ Found {len(results)} {test_type}")
        if results:
            print(f"   First item: {results[0].get('name', 'No name')} - {results[0].get('price', 'No price')}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Simple search failed: {e}")
        return False

def test_search_with_color():
    """Test search with color filter"""
    print("\n🔍 Testing search with color filter...")
    try:
        # Get available colors
        colors = get_available_colors_from_database()
        if not colors:
            print("❌ No colors available")
            return False
        
        # Test search with first available color
        test_color = colors[0]
        print(f"🔍 Searching for shirts with color {test_color}...")
        
        results = search_database_products(
            clothing_type='shirts',
            color=test_color,
            max_items=3
        )
        
        print(f"✅ Found {len(results)} shirts with color {test_color}")
        if results:
            print(f"   First item: {results[0].get('name', 'No name')} - {results[0].get('price', 'No price')}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Color search failed: {e}")
        return False

def test_outfit_search():
    """Test outfit search with AI prompt"""
    print("\n🎨 Testing outfit search with AI prompt...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return False
    
    try:
        prompt = "casual summer outfit with blue shirts and white pants"
        print(f"🔍 Searching for: '{prompt}'")
        
        results = search_outfit_from_prompt(api_key, prompt, top_results_per_item=3)
        
        if 'error' in results:
            print(f"❌ Outfit search failed: {results['error']}")
            return False
        
        print("✅ Outfit search completed!")
        print(f"   Outfit description: {results.get('outfit_response', {}).get('outfit_description', 'No description')}")
        print(f"   Total items found: {results.get('total_items_found', 0)}")
        
        # Debug: Show what the AI generated
        outfit_response = results.get('outfit_response', {})
        outfit_items = outfit_response.get('outfit_items', [])
        print(f"   AI generated {len(outfit_items)} outfit items:")
        for i, item in enumerate(outfit_items, 1):
            print(f"     {i}. {item.get('clothing_type', 'No type')} - Color: {item.get('color', 'No color')} - Filters: {item.get('filters', {})}")
        
        search_results = results.get('search_results', {})
        for clothing_type, products in search_results.items():
            print(f"   {clothing_type}: {len(products)} items")
            if products:
                print(f"     First item: {products[0].get('name', 'No name')} - {products[0].get('price', 'No price')}")
        
        return results.get('total_items_found', 0) > 0
        
    except Exception as e:
        print(f"❌ Outfit search failed: {e}")
        return False

def test_outfit_search_without_colors():
    """Test outfit search without color filters"""
    print("\n🎨 Testing outfit search without color filters...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return False
    
    try:
        prompt = "casual outfit with shirts and pants"
        print(f"🔍 Searching for: '{prompt}'")
        
        results = search_outfit_from_prompt(api_key, prompt, top_results_per_item=3)
        
        if 'error' in results:
            print(f"❌ Outfit search failed: {results['error']}")
            return False
        
        print("✅ Outfit search completed!")
        print(f"   Outfit description: {results.get('outfit_response', {}).get('outfit_description', 'No description')}")
        print(f"   Total items found: {results.get('total_items_found', 0)}")
        
        search_results = results.get('search_results', {})
        for clothing_type, products in search_results.items():
            print(f"   {clothing_type}: {len(products)} items")
            if products:
                print(f"     First item: {products[0].get('name', 'No name')} - {products[0].get('price', 'No price')}")
        
        return results.get('total_items_found', 0) > 0
        
    except Exception as e:
        print(f"❌ Outfit search failed: {e}")
        return False

def test_ai_generated_values():
    """Test the exact values that the AI generated"""
    print("\n🔍 Testing AI generated values directly...")
    
    try:
        # Test cornflowerblue shirts (what AI generated before)
        print("🔍 Testing cornflowerblue shirts...")
        results = search_database_products(
            clothing_type='shirts',
            color='cornflowerblue',
            max_items=3
        )
        print(f"✅ Found {len(results)} cornflowerblue shirts")
        if results:
            print(f"   First item: {results[0].get('name', 'No name')} - {results[0].get('price', 'No price')}")
        
        # Test lightsteelblue shirts (what AI generated now)
        print("🔍 Testing lightsteelblue shirts...")
        results = search_database_products(
            clothing_type='shirts',
            color='lightsteelblue',
            max_items=3
        )
        print(f"✅ Found {len(results)} lightsteelblue shirts")
        if results:
            print(f"   First item: {results[0].get('name', 'No name')} - {results[0].get('price', 'No price')}")
        
        # Test whitesmoke pants (what AI generated)
        print("🔍 Testing whitesmoke pants...")
        results = search_database_products(
            clothing_type='pants',
            color='whitesmoke',
            max_items=3
        )
        print(f"✅ Found {len(results)} whitesmoke pants")
        if results:
            print(f"   First item: {results[0].get('name', 'No name')} - {results[0].get('price', 'No price')}")
        
        # Test shirts without color
        print("🔍 Testing shirts without color...")
        results = search_database_products(
            clothing_type='shirts',
            max_items=3
        )
        print(f"✅ Found {len(results)} shirts (no color filter)")
        if results:
            print(f"   First item: {results[0].get('name', 'No name')} - {results[0].get('price', 'No price')}")
        
        # Test pants without color
        print("🔍 Testing pants without color...")
        results = search_database_products(
            clothing_type='pants',
            max_items=3
        )
        print(f"✅ Found {len(results)} pants (no color filter)")
        if results:
            print(f"   First item: {results[0].get('name', 'No name')} - {results[0].get('price', 'No price')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct search failed: {e}")
        return False

def test_colors_by_clothing_type():
    """Test what colors are available for specific clothing types"""
    print("\n🎨 Testing colors by clothing type...")
    
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'data_collection'))
        from supabase_db import SupabaseDB
        
        db_client = SupabaseDB()
        
        # Test shirts colors
        print("🔍 Testing shirt colors...")
        response = db_client.client.table('clothes_db').select('dominant_tone').eq('clothing_type', 'shirts').not_.is_('dominant_tone', 'null').execute()
        shirt_colors = list(set([item.get('dominant_tone') for item in response.data if item.get('dominant_tone')]))
        print(f"✅ Shirt colors: {shirt_colors}")
        
        # Test pants colors
        print("🔍 Testing pants colors...")
        response = db_client.client.table('clothes_db').select('dominant_tone').eq('clothing_type', 'pants').not_.is_('dominant_tone', 'null').execute()
        pants_colors = list(set([item.get('dominant_tone') for item in response.data if item.get('dominant_tone')]))
        print(f"✅ Pants colors: {pants_colors}")
        
        return shirt_colors, pants_colors
        
    except Exception as e:
        print(f"❌ Failed to get colors by type: {e}")
        return [], []

def main():
    """Run all tests"""
    print("🧪 Testing Fashion App Outfit Search")
    print("=" * 50)
    
    # Test database connection
    if not test_database_connection():
        return
    
    # Test available clothing types
    clothing_types = test_available_clothing_types()
    if not clothing_types:
        return
    
    # Test available colors
    colors = test_available_colors()
    if not colors:
        return
    
    # Test dominant_hue field
    test_dominant_hue_field()
    
    # Test colors by clothing type
    test_colors_by_clothing_type()
    
    # Test simple search
    if not test_simple_search():
        return
    
    # Test search with color
    test_search_with_color()
    
    # Test AI generated values directly
    test_ai_generated_values()
    
    # Test outfit search
    test_outfit_search()
    
    # Test outfit search without colors
    test_outfit_search_without_colors()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 