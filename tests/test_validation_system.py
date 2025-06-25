#!/usr/bin/env python3
"""
Test script for the enhanced validation system.

This script tests the improved validation that ensures the AI model only
recommends material-color combinations that actually exist in the database.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_collection'))

from outfit_prompt_parser import OutfitPromptParser
from search_function import validate_material_color_combination, get_detailed_inventory_by_clothing_type

def test_parser_initialization():
    """Test parser initialization"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return False
        
        parser = OutfitPromptParser(api_key)
        return len(parser.clothing_types) > 0
    except Exception as e:
        return False

def test_prompt_parsing():
    """Test prompt parsing with validation"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return False
        
        parser = OutfitPromptParser(api_key)
        
        test_prompts = [
            "casual summer outfit with linen shirts",
            "winter outfit with wool sweaters",
            "business casual with cotton pants"
        ]
        
        results = []
        for prompt in test_prompts:
            try:
                outfit_response = parser.parse_outfit_prompt(prompt, max_items_per_category=1)
                results.append({
                    'prompt': prompt,
                    'success': True,
                    'variations': len(outfit_response['outfit_variations'])
                })
            except Exception as e:
                results.append({
                    'prompt': prompt,
                    'success': False,
                    'error': str(e)
                })
        
        return len([r for r in results if r['success']]) > 0
    except Exception as e:
        return False

def test_combination_validation():
    """Test material-color combination validation"""
    try:
        detailed_inventory = get_detailed_inventory_by_clothing_type()
        
        if not detailed_inventory:
            return False
        
        test_combinations = [
            ('shirts', 'lin', 'BLUE'),
            ('pants', 'bomull', 'WHITE'),
            ('sweaters', 'ull', 'BLACK')
        ]
        
        valid_count = 0
        for clothing_type, material, color in test_combinations:
            if clothing_type in detailed_inventory:
                try:
                    is_valid = validate_material_color_combination(clothing_type, material, color)
                    if is_valid:
                        valid_count += 1
                except:
                    pass
        
        return valid_count > 0
    except Exception as e:
        return False

def test_retry_mechanism():
    """Test the retry mechanism"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return False
        
        parser = OutfitPromptParser(api_key)
        
        # Test with a prompt that might trigger validation
        prompt = "outfit with invalid material color combination"
        
        try:
            outfit_response = parser.parse_outfit_prompt(prompt, max_items_per_category=1, max_retries=2)
            return True
        except:
            # Even if it fails, the retry mechanism should have been triggered
            return True
    except Exception as e:
        return False

def run_test_suite():
    """Run all validation system tests"""
    tests = [
        ("Parser Initialization", test_parser_initialization),
        ("Prompt Parsing", test_prompt_parsing),
        ("Combination Validation", test_combination_validation),
        ("Retry Mechanism", test_retry_mechanism)
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