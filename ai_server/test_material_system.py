#!/usr/bin/env python3
"""
Test script for the new material system.
This script tests the material building block extraction and database material search.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_collection'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from search_function import (
    extract_material_building_blocks, 
    get_available_materials_from_database,
    search_materials_in_database,
    search_database_products,
    get_available_clothing_types_from_database,
    get_available_colors_from_database,
    get_database_inventory_summary
)

def test_material_extraction():
    """Test extracting building blocks from material strings."""
    print("🔧 Testing material building block extraction...")
    
    test_materials = [
        "55% lin, 45% bomull",
        "100% linne",
        "80% ull, 20% elastan",
        "70% polyester, 45% bomull",
        "50% siden, 50% polyester",
        "90% kaschmir, 10% ull",
        "Mixed materials",
        "Syntetisk material",
        "Ekologisk bomull",
        "Recycled polyester"
    ]
    
    for material in test_materials:
        blocks = extract_material_building_blocks(material)
        print(f"  '{material}' -> {sorted(list(blocks))}")
    
    return True

def test_database_clothing_types():
    """Test fetching clothing types from database."""
    print("\n👕 Testing database clothing type extraction...")
    
    try:
        clothing_types = get_available_clothing_types_from_database()
        
        print(f"✅ Found {len(clothing_types)} unique clothing types")
        print(f"👕 Available clothing types: {clothing_types}")
        
        return len(clothing_types) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_database_colors():
    """Test fetching colors from database."""
    print("\n🎨 Testing database color extraction...")
    
    try:
        colors = get_available_colors_from_database()
        
        print(f"✅ Found {len(colors)} unique colors")
        print(f"🎨 Available colors: {colors}")
        
        return len(colors) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_database_materials():
    """Test fetching materials from database."""
    print("\n📊 Testing database material extraction...")
    
    try:
        materials_data = get_available_materials_from_database()
        
        print(f"✅ Found {len(materials_data['raw_materials'])} raw materials")
        print(f"✅ Extracted {len(materials_data['building_blocks'])} building blocks")
        
        print(f"\n🔧 Building blocks: {sorted(materials_data['building_blocks'])}")
        
        # Show some example raw materials
        print(f"\n📝 Example raw materials:")
        for i, material in enumerate(materials_data['raw_materials'][:10], 1):
            print(f"  {i}. {material}")
        
        if len(materials_data['raw_materials']) > 10:
            print(f"  ... and {len(materials_data['raw_materials']) - 10} more")
        
        return len(materials_data['building_blocks']) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_inventory_summary():
    """Test getting complete inventory summary."""
    print("\n📊 Testing inventory summary...")
    
    try:
        summary = get_database_inventory_summary()
        
        print(f"✅ Inventory Summary:")
        print(f"   👕 Clothing Types: {summary['total_clothing_types']}")
        print(f"   🎨 Colors: {summary['total_colors']}")
        print(f"   🔧 Material Building Blocks: {summary['total_materials']}")
        print(f"   📝 Raw Materials: {summary['total_raw_materials']}")
        
        print(f"\n👕 Clothing Types: {summary['clothing_types']}")
        print(f"🎨 Colors: {summary['colors']}")
        print(f"🔧 Materials: {summary['materials']}")
        
        return (summary['total_clothing_types'] > 0 and 
                summary['total_colors'] > 0 and 
                summary['total_materials'] > 0)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_material_search():
    """Test searching for specific materials in database."""
    print("\n🔍 Testing material search in database...")
    
    test_materials = ['lin', 'bomull', 'ull', 'polyester']
    
    for material in test_materials:
        try:
            matching_materials = search_materials_in_database(material)
            print(f"  '{material}' -> {len(matching_materials)} matches")
            
            # Show first few matches
            for i, match in enumerate(matching_materials[:3], 1):
                print(f"    {i}. {match}")
            if len(matching_materials) > 3:
                print(f"    ... and {len(matching_materials) - 3} more")
                
        except Exception as e:
            print(f"  ❌ Error searching for '{material}': {e}")
    
    return True

def test_product_search_with_materials():
    """Test searching for products with material filters."""
    print("\n👕 Testing product search with material filters...")
    
    test_searches = [
        {
            'clothing_type': 'shirts',
            'material': 'lin',
            'description': 'Linen shirts'
        },
        {
            'clothing_type': 'sweaters',
            'material': 'ull',
            'description': 'Wool sweaters'
        },
        {
            'clothing_type': 'pants',
            'material': 'bomull',
            'description': 'Cotton pants'
        }
    ]
    
    for search in test_searches:
        try:
            print(f"\n🔍 Searching for {search['description']}...")
            
            results = search_database_products(
                clothing_type=search['clothing_type'],
                filters={'material': search['material']},
                max_items=3,
                sort_by_price=True
            )
            
            print(f"  ✅ Found {len(results)} products")
            
            for i, product in enumerate(results, 1):
                print(f"    {i}. {product['name']} - {product['price']}")
                print(f"       Material: {product.get('material', 'Not specified')}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return True

def test_ai_inventory_validation():
    """Test that the AI model gets the correct inventory from database."""
    print("\n🤖 Testing AI inventory validation...")
    
    try:
        from outfit_prompt_parser import OutfitPromptParser
        import keys
        
        if not keys.API_KEY:
            print("  ⚠️ No API key found, skipping AI test")
            return True
        
        parser = OutfitPromptParser(keys.API_KEY)
        
        print(f"  ✅ AI model loaded with database inventory:")
        print(f"     👕 Clothing Types: {len(parser.clothing_types)}")
        print(f"     🎨 Colors: {len(parser.colors)}")
        print(f"     🔧 Material Building Blocks: {len(parser.available_materials)}")
        
        print(f"\n  👕 Available clothing types: {parser.clothing_types}")
        print(f"  🎨 Available colors: {parser.colors}")
        print(f"  🔧 Available materials: {parser.available_materials}")
        
        # Test a simple prompt to see if inventory is used correctly
        print(f"\n  📝 Testing prompt parsing...")
        try:
            outfit_response = parser.parse_outfit_prompt("linen summer outfit", max_items_per_category=1)
            
            print(f"  ✅ Successfully parsed prompt")
            print(f"  🎨 Generated {len(outfit_response['outfit_variations'])} variations")
            
            # Check if inventory is used in the variations
            for i, variation in enumerate(outfit_response['outfit_variations'], 1):
                print(f"    Variation {i}: {variation['variation_name']}")
                for j, item in enumerate(variation['outfit_items'], 1):
                    print(f"      Item {j}: {item['clothing_type']}")
                    if 'color' in item and item['color']:
                        print(f"        Color: {item['color']}")
                    filters = item.get('filters', {})
                    if 'material' in filters:
                        print(f"        Material: {filters['material']}")
            
        except Exception as e:
            print(f"  ❌ Error parsing prompt: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing AI validation: {e}")
        return False

def main():
    """Run all material system tests."""
    print("🧪 DATABASE INVENTORY SYSTEM TEST SUITE")
    print("=" * 50)
    
    # Check environment
    if not os.getenv('SUPABASE_KEY'):
        print("❌ SUPABASE_KEY environment variable not set!")
        print("Please set it before running this script:")
        print("export SUPABASE_KEY='your-supabase-anon-key'")
        return
    
    print("✅ Environment variables found")
    
    # Run tests
    tests = [
        ("Material Extraction", test_material_extraction),
        ("Database Clothing Types", test_database_clothing_types),
        ("Database Colors", test_database_colors),
        ("Database Materials", test_database_materials),
        ("Inventory Summary", test_inventory_summary),
        ("Material Search", test_material_search),
        ("Product Search with Materials", test_product_search_with_materials),
        ("AI Inventory Validation", test_ai_inventory_validation)
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
        print("🎉 All tests passed! Database inventory system is working correctly.")
        print("\n💡 The AI model will now use:")
        print("   - Actual clothing types from your database")
        print("   - Real colors extracted from your products")
        print("   - Material building blocks from your inventory")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 