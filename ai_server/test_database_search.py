#!/usr/bin/env python3
"""
Test script for database search functionality.
This script tests the new database-based search functions.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_collection'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from search_function import (
    search_database_products, 
    search_outfit, 
    get_database_stats,
    get_database_inventory_summary,
    get_available_clothing_types_from_database,
    get_available_colors_from_database,
    get_available_materials_from_database
)
from outfit_prompt_parser import OutfitPromptParser
import keys

def test_database_connection():
    """Test database connection and get stats."""
    print("🔍 Testing database connection...")
    
    try:
        stats = get_database_stats()
        print(f"✅ Database connection successful!")
        print(f"📊 Database stats: {stats}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_inventory_extraction():
    """Test extracting inventory data from database."""
    print("\n📊 Testing inventory extraction...")
    
    try:
        # Test individual extraction functions
        clothing_types = get_available_clothing_types_from_database()
        colors = get_available_colors_from_database()
        materials_data = get_available_materials_from_database()
        
        print(f"✅ Found {len(clothing_types)} clothing types")
        print(f"✅ Found {len(colors)} colors")
        print(f"✅ Found {len(materials_data.get('building_blocks', []))} material building blocks")
        
        # Test comprehensive summary
        summary = get_database_inventory_summary()
        print(f"✅ Inventory summary: {summary['total_clothing_types']} types, {summary['total_colors']} colors, {summary['total_materials']} materials")
        
        return (len(clothing_types) > 0 and len(colors) > 0 and len(materials_data.get('building_blocks', [])) > 0)
        
    except Exception as e:
        print(f"❌ Inventory extraction failed: {e}")
        return False

def test_single_product_search():
    """Test searching for a single product type."""
    print("\n🔍 Testing single product search...")
    
    try:
        # Get available clothing types first
        clothing_types = get_available_clothing_types_from_database()
        colors = get_available_colors_from_database()
        
        if not clothing_types:
            print("  ⚠️ No clothing types available, skipping product search")
            return True
        
        # Use the first available clothing type and color
        test_clothing_type = clothing_types[0]
        test_color = colors[0] if colors else None
        
        print(f"  🔍 Testing search for {test_clothing_type}" + (f" in {test_color}" if test_color else ""))
        
        # Test search
        results = search_database_products(
            clothing_type=test_clothing_type,
            color=test_color,
            max_items=5,
            sort_by_price=True
        )
        
        print(f"  ✅ Found {len(results)} products")
        for i, product in enumerate(results, 1):
            print(f"    {i}. {product['name']} - {product['price']}")
        
        return len(results) > 0
    except Exception as e:
        print(f"❌ Single product search failed: {e}")
        return False

def test_outfit_search():
    """Test searching for an outfit."""
    print("\n👕 Testing outfit search...")
    
    try:
        # Get available inventory
        clothing_types = get_available_clothing_types_from_database()
        colors = get_available_colors_from_database()
        
        if len(clothing_types) < 2:
            print("  ⚠️ Need at least 2 clothing types for outfit search")
            return True
        
        outfit_items = [
            {
                'clothing_type': clothing_types[0],
                'color': colors[0] if colors else None,
                'max_items': 5
            },
            {
                'clothing_type': clothing_types[1],
                'color': colors[1] if len(colors) > 1 else None,
                'max_items': 5
            }
        ]
        
        outfit_results = search_outfit(outfit_items, top_results_per_item=3)
        
        print(f"✅ Outfit search completed!")
        for clothing_type, products in outfit_results.items():
            print(f"  {clothing_type}: {len(products)} products")
            for i, product in enumerate(products[:2], 1):  # Show first 2 products
                print(f"    {i}. {product['name']} - {product['price']}")
        
        return len(outfit_results) > 0
    except Exception as e:
        print(f"❌ Outfit search failed: {e}")
        return False

def test_ai_prompt_parsing():
    """Test AI prompt parsing and search."""
    print("\n🤖 Testing AI prompt parsing...")
    
    try:
        # Initialize parser
        parser = OutfitPromptParser(keys.API_KEY)
        
        # Test prompt
        prompt = "minimalist summer outfit with neutral colors"
        
        print(f"📝 Testing prompt: '{prompt}'")
        print(f"🔧 AI model loaded with:")
        print(f"   👕 {len(parser.clothing_types)} clothing types")
        print(f"   🎨 {len(parser.colors)} colors")
        print(f"   🔧 {len(parser.available_materials)} material building blocks")
        
        # Parse the prompt
        outfit_response = parser.parse_outfit_prompt(prompt)
        
        print(f"✅ AI generated {len(outfit_response['outfit_variations'])} outfit variations:")
        for i, variation in enumerate(outfit_response['outfit_variations'], 1):
            print(f"  {i}. {variation['variation_name']}")
            print(f"     {variation['variation_description']}")
        
        # Search for the outfit
        results = parser.search_outfit_from_prompt(
            prompt=prompt,
            top_results_per_item=2,
            sort_by_price=True
        )
        
        print(f"✅ AI outfit search completed!")
        for variation_name, variation_data in results.items():
            products = variation_data['products']
            total_products = sum(len(products[ct]) for ct in products if products[ct])
            print(f"  {variation_name}: {total_products} total products")
        
        return len(results) > 0
    except Exception as e:
        print(f"❌ AI prompt parsing failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 DATABASE SEARCH TEST SUITE")
    print("=" * 50)
    
    # Check environment
    if not os.getenv('SUPABASE_KEY'):
        print("❌ SUPABASE_KEY environment variable not set!")
        print("Please set it before running this script:")
        print("export SUPABASE_KEY='your-supabase-anon-key'")
        return
    
    if not keys.API_KEY:
        print("❌ API_KEY not found in keys.py!")
        print("Please add your OpenAI API key to keys.py")
        return
    
    print("✅ Environment variables found")
    
    # Run tests
    tests = [
        ("Database Connection", test_database_connection),
        ("Inventory Extraction", test_inventory_extraction),
        ("Single Product Search", test_single_product_search),
        ("Outfit Search", test_outfit_search),
        ("AI Prompt Parsing", test_ai_prompt_parsing)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Database search is working correctly.")
        print("\n💡 The AI model now uses your actual database inventory:")
        print("   - Real clothing types from your products")
        print("   - Actual colors extracted from your items")
        print("   - Material building blocks from your inventory")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 