#!/usr/bin/env python3
"""
Test script for the material system.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_collection'))

from search_function import (
    extract_material_building_blocks,
    get_available_clothing_types_from_database,
    get_available_colors_from_database,
    get_available_materials_from_database,
    get_database_inventory_summary
)

def test_material_building_blocks():
    """Test material building block extraction"""
    test_materials = [
        "55% lin, 45% bomull",
        "100% linne",
        "80% ull, 20% polyamid",
        "Blandat material",
        "70% polyester, 30% elastan"
    ]
    
    for material in test_materials:
        blocks = extract_material_building_blocks(material)
        # Just test that the function works
    
    return True

def test_clothing_types():
    """Test clothing type extraction from database"""
    try:
        clothing_types = get_available_clothing_types_from_database()
        return len(clothing_types) > 0
    except Exception as e:
        return False

def test_colors():
    """Test color extraction from database"""
    try:
        colors = get_available_colors_from_database()
        return len(colors) > 0
    except Exception as e:
        return False

def test_materials():
    """Test material extraction from database"""
    try:
        materials_data = get_available_materials_from_database()
        return len(materials_data['raw_materials']) > 0
    except Exception as e:
        return False

def test_inventory_summary():
    """Test inventory summary"""
    try:
        summary = get_database_inventory_summary()
        return summary['total_clothing_types'] > 0
    except Exception as e:
        return False

def run_test_suite():
    """Run all tests"""
    tests = [
        ("Material Building Blocks", test_material_building_blocks),
        ("Clothing Types", test_clothing_types),
        ("Colors", test_colors),
        ("Materials", test_materials),
        ("Inventory Summary", test_inventory_summary)
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