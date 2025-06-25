#!/usr/bin/env python3
"""
Test Relevance Scoring

This script demonstrates the new relevance scoring functionality in the search system.
"""

import sys
import os

# Add the ai_server directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_server'))

from search_function import (
    search_database_products, 
    search_products_by_text, 
    test_relevance_scoring,
    calculate_product_relevance_score
)

def main():
    """
    Demonstrate the relevance scoring functionality with various test cases.
    """
    print("🔍 Testing Relevance Scoring System")
    print("=" * 50)
    
    # Test 1: Compare relevance scoring vs price-based sorting
    print("\n1️⃣ Comparing Relevance Scoring vs Price-Based Sorting")
    print("-" * 45)
    
    try:
        # Search with relevance scoring
        relevance_results = search_database_products(
            'sweaters',
            filters={'material': 'lin'},
            color='BLUE',
            search_terms=['crewneck'],
            max_items=3,
            use_relevance_scoring=True
        )
        
        # Search with price sorting
        price_results = search_database_products(
            'sweaters',
            filters={'material': 'lin'},
            color='BLUE',
            search_terms=['crewneck'],
            max_items=3,
            use_relevance_scoring=False,
            sort_by_price=True
        )
        
        print(f"Found {len(relevance_results)} products with relevance scoring")
        print(f"Found {len(price_results)} products with price sorting")
        
        if relevance_results:
            print("\n🎯 Top relevance-scored results:")
            for i, product in enumerate(relevance_results[:3], 1):
                print(f"  {i}. {product.get('name', 'Unknown')[:50]}...")
                print(f"     Relevance Score: {product.get('relevance_score', 0):.1f}/100")
                print(f"     Material: {product.get('material', 'Unknown')[:30]}")
                print(f"     Color: {product.get('dominant_tone', 'Unknown')}")
                print(f"     Price: {product.get('price', 'Unknown')}")
                print()
        
    except Exception as e:
        print(f"❌ Error in test 1: {e}")
    
    # Test 2: Text search with different scoring weights
    print("\n2️⃣ Testing Custom Scoring Weights")
    print("-" * 35)
    
    try:
        # Emphasize search terms more
        search_focused_weights = {'material': 0.2, 'color': 0.2, 'search_terms': 0.6}
        
        search_results = search_products_by_text(
            search_terms=['crewneck', 'pullover'],
            clothing_type='sweaters',
            max_items=3,
            use_relevance_scoring=True,
            scoring_weights=search_focused_weights
        )
        
        print(f"Found {len(search_results)} products with search-focused weights")
        
        if search_results:
            print("\n🔤 Search-focused results:")
            for i, product in enumerate(search_results[:3], 1):
                print(f"  {i}. {product.get('name', 'Unknown')[:50]}...")
                print(f"     Relevance Score: {product.get('relevance_score', 0):.1f}/100")
                print()
        
    except Exception as e:
        print(f"❌ Error in test 2: {e}")
    
    # Test 3: Run comprehensive test
    print("\n3️⃣ Running Comprehensive Test Suite")
    print("-" * 35)
    
    try:
        test_results = test_relevance_scoring()
        
        if 'error' in test_results:
            print(f"❌ Test failed: {test_results['error']}")
        else:
            print("✅ Comprehensive test completed successfully!")
            
            relevance_results = test_results.get('relevance_scoring_results', {})
            print(f"   - Found {relevance_results.get('count', 0)} products with scoring")
            
            text_results = test_results.get('text_search_with_scoring', {})
            print(f"   - Found {text_results.get('count', 0)} products in text search")
            
            outfit_results = test_results.get('outfit_search_scoring', {})
            print(f"   - Found {outfit_results.get('total_items', 0)} items in outfit search")
            
            if relevance_results.get('top_scores'):
                print(f"   - Top score: {relevance_results['top_scores'][0].get('relevance_score', 0):.1f}/100")
    
    except Exception as e:
        print(f"❌ Error in test 3: {e}")
    
    # Test 4: Demonstrate individual product scoring
    print("\n4️⃣ Individual Product Scoring Example")
    print("-" * 38)
    
    try:
        # Get a sample product to score
        sample_products = search_database_products('sweaters', max_items=1, use_relevance_scoring=False)
        
        if sample_products:
            product = sample_products[0]
            
            # Score this product against different criteria
            score_1 = calculate_product_relevance_score(
                product=product,
                target_material='lin',
                target_color='BLUE',
                search_terms=['crewneck']
            )
            
            score_2 = calculate_product_relevance_score(
                product=product,
                search_terms=['casual', 'sweater']
            )
            
            print(f"Sample product: {product.get('name', 'Unknown')[:50]}...")
            print(f"Score for 'lin + BLUE + crewneck': {score_1:.1f}/100")
            print(f"Score for 'casual + sweater': {score_2:.1f}/100")
            print(f"Actual material: {product.get('material', 'Unknown')}")
            print(f"Actual color: {product.get('dominant_tone', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Error in test 4: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Relevance Scoring Test Complete!")
    print("\nThe new scoring system considers:")
    print("  • Material compatibility (using building blocks)")
    print("  • Color matching (with similarity heuristics)")
    print("  • Search term relevance (with fashion synonyms)")
    print("  • Customizable weights for different priorities")

if __name__ == "__main__":
    main() 