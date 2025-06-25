#!/usr/bin/env python3
"""
Test script for dynamic material building blocks and comprehensive AI data functionality.
This script demonstrates how the system can provide granular data to the AI for better decision-making.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_collection'))

from search_function import (
    build_dynamic_material_building_blocks,
    get_comprehensive_ai_data,
    get_ai_decision_support_data,
    get_material_color_availability_matrix,
    get_available_combinations_for_ai,
    validate_combination_exists,
    get_best_available_combinations,
    suggest_outfit_combinations
)

def test_dynamic_material_extraction():
    """Test dynamic material building blocks extraction"""
    print("=== Testing Dynamic Material Building Blocks ===")
    
    # Test dynamic material extraction
    dynamic_materials = build_dynamic_material_building_blocks()
    print(f"Found {len(dynamic_materials)} dynamic material building blocks:")
    print(sorted(list(dynamic_materials)))
    print()

def test_comprehensive_ai_data():
    """Test comprehensive AI data functionality"""
    print("=== Testing Comprehensive AI Data ===")
    
    # Get comprehensive data
    comprehensive_data = get_comprehensive_ai_data()
    
    print("Database Statistics:")
    stats = comprehensive_data.get('statistics', {})
    print(f"  Total Products: {stats.get('total_products', 0)}")
    print(f"  Clothing Types: {stats.get('total_clothing_types', 0)}")
    print(f"  Materials: {stats.get('total_materials', 0)}")
    print(f"  Colors: {stats.get('total_colors', 0)}")
    print(f"  Combinations: {stats.get('total_combinations', 0)}")
    print()
    
    print("Available Clothing Types:")
    clothing_types = comprehensive_data.get('clothing_types', [])
    for ct in clothing_types[:10]:  # Show first 10
        print(f"  - {ct}")
    if len(clothing_types) > 10:
        print(f"  ... and {len(clothing_types) - 10} more")
    print()
    
    print("Available Materials (Building Blocks):")
    materials = comprehensive_data.get('materials', {}).get('building_blocks', [])
    for material in materials[:15]:  # Show first 15
        print(f"  - {material}")
    if len(materials) > 15:
        print(f"  ... and {len(materials) - 15} more")
    print()
    
    print("Available Colors:")
    colors = comprehensive_data.get('colors', [])
    for color in colors[:10]:  # Show first 10
        print(f"  - {color}")
    if len(colors) > 10:
        print(f"  ... and {len(colors) - 10} more")
    print()

def test_availability_matrix():
    """Test material-color availability matrix"""
    print("=== Testing Material-Color Availability Matrix ===")
    
    matrix = get_material_color_availability_matrix()
    
    print("Material-Color Availability (Sample):")
    for clothing_type, materials in list(matrix.items())[:3]:
        print(f"\n{clothing_type.upper()}:")
        for material, colors in list(materials.items())[:3]:
            print(f"  {material}: {', '.join(colors[:5])}")
            if len(colors) > 5:
                print(f"    ... and {len(colors) - 5} more colors")
    print()

def test_ai_combinations():
    """Test AI combinations functionality"""
    print("=== Testing AI Combinations ===")
    
    combinations = get_available_combinations_for_ai()
    
    print("Available Combinations (Sample):")
    for clothing_type, combo_list in list(combinations.items())[:3]:
        print(f"\n{clothing_type.upper()}:")
        for combo in combo_list[:5]:
            print(f"  {combo['material']} + {combo['color']} ({combo['product_count']} products)")
        if len(combo_list) > 5:
            print(f"  ... and {len(combo_list) - 5} more combinations")
    print()

def test_combination_validation():
    """Test combination validation"""
    print("=== Testing Combination Validation ===")
    
    # Test some combinations
    test_combinations = [
        ('sweaters', 'lin', 'BLUE'),
        ('pants', 'bomull', 'BLACK'),
        ('shirts', 'polyester', 'WHITE'),
        ('t_shirts', 'bomull', 'RED')
    ]
    
    for clothing_type, material, color in test_combinations:
        exists, count = validate_combination_exists(clothing_type, material, color)
        status = "✓ EXISTS" if exists else "✗ NOT FOUND"
        print(f"{clothing_type} + {material} + {color}: {status} ({count} products)")
    print()

def test_best_combinations():
    """Test best available combinations"""
    print("=== Testing Best Available Combinations ===")
    
    # Test for sweaters with preferred materials
    best_combinations = get_best_available_combinations(
        'sweaters', 
        preferred_materials=['lin', 'bomull'], 
        min_products=1
    )
    
    print("Best Sweater Combinations (with preferred materials):")
    for combo in best_combinations[:5]:
        print(f"  {combo['material']} + {combo['color']} (Priority: {combo['priority_score']:.2f}, Products: {combo['product_count']})")
    print()

def test_ai_decision_support():
    """Test AI decision support data"""
    print("=== Testing AI Decision Support Data ===")
    
    ai_data = get_ai_decision_support_data()
    
    print("AI Decision Support Summary:")
    print(f"  Total Valid Combinations: {len(ai_data.get('all_valid_combinations', []))}")
    print(f"  Clothing Types: {len(ai_data.get('clothing_types', []))}")
    print(f"  Materials: {len(ai_data.get('materials', {}).get('building_blocks', []))}")
    print(f"  Colors: {len(ai_data.get('colors', []))}")
    print()
    
    print("Sample Valid Combinations:")
    sample_combinations = ai_data.get('examples', {}).get('sample_combinations', [])
    for combo in sample_combinations[:5]:
        print(f"  {combo['clothing_type']} + {combo['material']} + {combo['color']} ({combo['product_count']} products)")
    print()
    
    print("Most Common Materials:")
    common_materials = ai_data.get('examples', {}).get('most_common_materials', [])
    for material, count in common_materials[:5]:
        print(f"  {material}: {count} products")
    print()
    
    print("Most Common Colors:")
    common_colors = ai_data.get('examples', {}).get('most_common_colors', [])
    for color, count in common_colors[:5]:
        print(f"  {color}: {count} products")
    print()

def test_outfit_suggestions():
    """Test outfit combination suggestions"""
    print("=== Testing Outfit Combination Suggestions ===")
    
    # Test outfit suggestions
    suggestions = suggest_outfit_combinations(
        preferred_materials=['lin', 'bomull'],
        preferred_colors=['BLUE', 'BLACK', 'WHITE'],
        max_suggestions=3
    )
    
    print("Suggested Outfit Combinations:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion['outfit_type']} (Score: {suggestion['compatibility_score']:.2f})")
        print(f"   Top: {suggestion['top']['material']} + {suggestion['top']['color']} ({suggestion['top']['product_count']} products)")
        print(f"   Bottom: {suggestion['bottom']['material']} + {suggestion['bottom']['color']} ({suggestion['bottom']['product_count']} products)")
        print(f"   Total Products: {suggestion['total_products']}")
    print()

def main():
    """Run all tests"""
    print("Dynamic Material Building Blocks and AI Data Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_dynamic_material_extraction()
        test_comprehensive_ai_data()
        test_availability_matrix()
        test_ai_combinations()
        test_combination_validation()
        test_best_combinations()
        test_ai_decision_support()
        test_outfit_suggestions()
        
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 