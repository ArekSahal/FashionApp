#!/usr/bin/env python3
"""
Test script for the detailed inventory system.

This script tests the new functions that provide detailed information about
which materials and colors are available for each clothing type, including
valid material-color combinations.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_collection'))

from search_function import (
    get_detailed_inventory_by_clothing_type,
    get_available_combinations_for_clothing_type,
    validate_material_color_combination,
    get_database_stats
)

def test_detailed_inventory():
    """Test the detailed inventory system."""
    print("🔍 Testing detailed inventory system...")
    print("=" * 60)
    
    try:
        # Get database stats first
        stats = get_database_stats()
        print(f"📊 Database stats: {stats}")
        
        # Get detailed inventory
        detailed_inventory = get_detailed_inventory_by_clothing_type()
        
        if not detailed_inventory:
            print("❌ No detailed inventory data found")
            return False
        
        print(f"\n✅ Successfully retrieved detailed inventory for {len(detailed_inventory)} clothing types")
        
        # Display detailed inventory
        for clothing_type, data in detailed_inventory.items():
            print(f"\n👕 {clothing_type.upper()} ({data['product_count']} products):")
            print(f"   🔧 Materials ({len(data['materials'])}): {', '.join(data['materials'])}")
            print(f"   🎨 Colors ({len(data['colors'])}): {', '.join(data['colors'])}")
            
            if data['material_color_combinations']:
                print(f"   🔗 Material-Color combinations:")
                for material, colors in data['material_color_combinations'].items():
                    if colors:  # Only show materials that have colors
                        print(f"      {material}: {', '.join(colors)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing detailed inventory: {e}")
        return False

def test_specific_clothing_type():
    """Test getting combinations for a specific clothing type."""
    print(f"\n🔍 Testing specific clothing type combinations...")
    print("=" * 60)
    
    try:
        # Test with a few clothing types
        test_types = ['shirts', 'pants', 'sweaters']
        
        for clothing_type in test_types:
            print(f"\n👕 Testing {clothing_type}:")
            
            combinations = get_available_combinations_for_clothing_type(clothing_type)
            
            if combinations['product_count'] == 0:
                print(f"   ⚠️ No products found for {clothing_type}")
                continue
            
            print(f"   📊 {combinations['product_count']} products")
            print(f"   🔧 Materials: {', '.join(combinations['materials'])}")
            print(f"   🎨 Colors: {', '.join(combinations['colors'])}")
            
            if combinations['material_color_combinations']:
                print(f"   🔗 Valid combinations:")
                for material, colors in combinations['material_color_combinations'].items():
                    if colors:
                        print(f"      {material}: {', '.join(colors)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing specific clothing type: {e}")
        return False

def test_combination_validation():
    """Test the material-color combination validation."""
    print(f"\n🔍 Testing combination validation...")
    print("=" * 60)
    
    try:
        # Get detailed inventory first
        detailed_inventory = get_detailed_inventory_by_clothing_type()
        
        if not detailed_inventory:
            print("❌ No detailed inventory available for testing")
            return False
        
        # Test some combinations
        test_combinations = [
            ('shirts', 'lin', 'BLUE'),
            ('pants', 'bomull', 'BLACK'),
            ('sweaters', 'ull', 'GRAY'),
            ('shirts', 'nonexistent_material', 'BLUE'),  # Should fail
            ('nonexistent_type', 'lin', 'BLUE'),  # Should fail
        ]
        
        for clothing_type, material, color in test_combinations:
            is_valid = validate_material_color_combination(clothing_type, material, color)
            status = "✅ Valid" if is_valid else "❌ Invalid"
            print(f"   {clothing_type} + {material} + {color}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing combination validation: {e}")
        return False

def test_inventory_formatting():
    """Test the inventory formatting for AI prompts."""
    print(f"\n🔍 Testing inventory formatting for AI...")
    print("=" * 60)
    
    try:
        from outfit_prompt_parser import OutfitPromptParser
        import keys
        
        # Initialize parser (this will load the detailed inventory)
        parser = OutfitPromptParser(keys.API_KEY)
        
        # Test the formatting function
        formatted_inventory = parser._format_detailed_inventory_for_ai()
        
        print("📝 Formatted inventory for AI:")
        print(formatted_inventory)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing inventory formatting: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 DETAILED INVENTORY SYSTEM TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Detailed Inventory", test_detailed_inventory),
        ("Specific Clothing Type", test_specific_clothing_type),
        ("Combination Validation", test_combination_validation),
        ("Inventory Formatting", test_inventory_formatting),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print(f"\n{'='*80}")
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The detailed inventory system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 