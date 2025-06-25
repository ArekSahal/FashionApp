#!/usr/bin/env python3
"""
Test script for the enhanced text search functionality in search_function.py
This script demonstrates how to use the new search_terms parameter and search_products_by_text function.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data_collection'))

from search_function import (
    search_database_products, 
    search_products_by_text, 
    search_outfit,
    get_database_stats
)

def test_basic_text_search():
    """Test basic text search functionality"""
    print("=== Testing Basic Text Search ===")
    
    # Test 1: Search for crewneck sweaters
    print("\n1. Searching for 'crewneck' sweaters:")
    results = search_database_products('sweaters', search_terms=['crewneck'], max_items=5)
    print(f"Found {len(results)} crewneck sweaters")
    for i, product in enumerate(results, 1):
        print(f"  {i}. {product.get('name', 'N/A')} - {product.get('price', 'N/A')}")
    
    # Test 2: Search for blue crewneck sweaters
    print("\n2. Searching for blue 'crewneck' sweaters:")
    results = search_database_products('sweaters', color='BLUE', search_terms=['crewneck'], max_items=5)
    print(f"Found {len(results)} blue crewneck sweaters")
    for i, product in enumerate(results, 1):
        print(f"  {i}. {product.get('name', 'N/A')} - {product.get('dominant_tone', 'N/A')} - {product.get('price', 'N/A')}")

def test_advanced_text_search():
    """Test advanced text search functionality"""
    print("\n=== Testing Advanced Text Search ===")
    
    # Test 1: Search for linen blue sweaters using advanced search
    print("\n1. Advanced search for 'lin' and 'blue' sweaters:")
    results = search_products_by_text(['lin', 'blue'], clothing_type='sweaters', max_items=5)
    print(f"Found {len(results)} linen blue sweaters")
    for i, product in enumerate(results, 1):
        print(f"  {i}. {product.get('name', 'N/A')} - Score: {product.get('search_score', 0)} - {product.get('price', 'N/A')}")
    
    # Test 2: Search for cotton t-shirts
    print("\n2. Advanced search for 'cotton' t-shirts:")
    results = search_products_by_text(['cotton'], clothing_type='t_shirts', max_items=5)
    print(f"Found {len(results)} cotton t-shirts")
    for i, product in enumerate(results, 1):
        print(f"  {i}. {product.get('name', 'N/A')} - Score: {product.get('search_score', 0)} - {product.get('price', 'N/A')}")
    
    # Test 3: Search for specific style terms
    print("\n3. Advanced search for 'v-neck' sweaters:")
    results = search_products_by_text(['v-neck', 'v neck'], clothing_type='sweaters', max_items=5)
    print(f"Found {len(results)} v-neck sweaters")
    for i, product in enumerate(results, 1):
        print(f"  {i}. {product.get('name', 'N/A')} - Score: {product.get('search_score', 0)} - {product.get('price', 'N/A')}")

def test_outfit_search_with_text():
    """Test outfit search with text search terms"""
    print("\n=== Testing Outfit Search with Text ===")
    
    # Test outfit search with specific text terms
    outfit_items = [
        {
            'clothing_type': 'sweaters', 
            'color': 'BLUE', 
            'search_terms': ['crewneck']
        },
        {
            'clothing_type': 'pants', 
            'color': 'BLACK', 
            'search_terms': ['jeans']
        }
    ]
    
    results = search_outfit(outfit_items, top_results_per_item=3)
    
    print("Outfit search results:")
    for clothing_type, products in results.items():
        print(f"\n{clothing_type.upper()}:")
        for i, product in enumerate(products, 1):
            print(f"  {i}. {product.get('name', 'N/A')} - {product.get('price', 'N/A')}")

def test_material_and_style_search():
    """Test searching for specific materials and styles"""
    print("\n=== Testing Material and Style Search ===")
    
    # Test 1: Search for wool sweaters
    print("\n1. Searching for wool sweaters:")
    results = search_products_by_text(['ull', 'wool'], clothing_type='sweaters', max_items=5)
    print(f"Found {len(results)} wool sweaters")
    for i, product in enumerate(results, 1):
        print(f"  {i}. {product.get('name', 'N/A')} - Material: {product.get('material', 'N/A')} - {product.get('price', 'N/A')}")
    
    # Test 2: Search for specific style terms
    print("\n2. Searching for 'turtleneck' sweaters:")
    results = search_products_by_text(['turtleneck', 'mock neck'], clothing_type='sweaters', max_items=5)
    print(f"Found {len(results)} turtleneck sweaters")
    for i, product in enumerate(results, 1):
        print(f"  {i}. {product.get('name', 'N/A')} - {product.get('price', 'N/A')}")

def main():
    """Main test function"""
    print("Testing Enhanced Text Search Functionality")
    print("=" * 50)
    
    # Check database connection
    try:
        stats = get_database_stats()
        print(f"Database contains {stats.get('total_products', 0)} products")
    except Exception as e:
        print(f"Database connection failed: {e}")
        return
    
    # Run tests
    try:
        test_basic_text_search()
        test_advanced_text_search()
        test_outfit_search_with_text()
        test_material_and_style_search()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 