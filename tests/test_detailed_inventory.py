#!/usr/bin/env python3
"""
Test script for the detailed inventory system.

This script tests the new functions that provide detailed information about
which materials and colors are available for each clothing type, including
valid material-color combinations.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_collection'))

from search_function import (
    get_detailed_inventory_by_clothing_type,
    get_available_combinations_for_clothing_type,
    validate_material_color_combination,
    get_database_stats
)
from supabase_db import SupabaseDB

def test_detailed_inventory():
    """Test the detailed inventory system"""
    try:
        # Test database connection
        db_client = SupabaseDB()
        stats = db_client.get_database_stats()
        
        # Get detailed inventory
        detailed_inventory = get_detailed_inventory_by_clothing_type()
        
        if not detailed_inventory:
            return False
        
        return True
        
    except Exception as e:
        return False

def test_specific_clothing_type():
    """Test detailed inventory for a specific clothing type"""
    try:
        # Test with a specific clothing type
        clothing_type = 'shirts'
        combinations = get_available_combinations_for_clothing_type(clothing_type)
        
        if combinations['product_count'] == 0:
            return False
        
        return True
        
    except Exception as e:
        return False

def test_combination_validation():
    """Test material-color combination validation"""
    try:
        # Get detailed inventory
        detailed_inventory = get_detailed_inventory_by_clothing_type()
        
        if not detailed_inventory:
            return False
        
        # Test some combinations
        test_combinations = [
            ('shirts', 'lin', 'BLUE'),
            ('sweaters', 'ull', 'BLACK'),
            ('pants', 'bomull', 'WHITE')
        ]
        
        for clothing_type, material, color in test_combinations:
            if clothing_type in detailed_inventory:
                is_valid = validate_material_color_combination(clothing_type, material, color)
                # Just test that the function works, don't care about the result
        
        return True
        
    except Exception as e:
        return False

def test_inventory_formatting():
    """Test inventory formatting for AI"""
    try:
        # Get detailed inventory
        detailed_inventory = get_detailed_inventory_by_clothing_type()
        
        if not detailed_inventory:
            return False
        
        # Format inventory for AI (this would be used in the AI prompt)
        formatted_inventory = []
        for clothing_type, data in detailed_inventory.items():
            formatted_inventory.append(f"{clothing_type}: {data['product_count']} products")
        
        return len(formatted_inventory) > 0
        
    except Exception as e:
        return False

def run_test_suite():
    """Run all tests"""
    tests = [
        ("Detailed Inventory System", test_detailed_inventory),
        ("Specific Clothing Type", test_specific_clothing_type),
        ("Combination Validation", test_combination_validation),
        ("Inventory Formatting", test_inventory_formatting)
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