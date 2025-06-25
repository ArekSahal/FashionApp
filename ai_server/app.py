#!/usr/bin/env python3
"""
Flask server for AI-powered outfit search.
Takes natural language outfit descriptions and returns structured outfit recommendations.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from outfit_prompt_parser import OutfitPromptParser
import search_function
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import Config
import logging
from datetime import datetime
import traceback

# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('outfit_server.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize the outfit parser
try:
    parser = OutfitPromptParser(Config.OPENAI_API_KEY)
    logger.info("✅ OutfitPromptParser initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize OutfitPromptParser: {e}")
    logger.info("⚠️ Server will start in limited mode without database connection")
    parser = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'parser_ready': parser is not None,
        'database_connected': parser is not None and hasattr(parser, 'clothing_types') and len(parser.clothing_types) > 0,
        'server_mode': 'full' if parser is not None else 'limited',
        'message': 'Server is running. Database connection required for full functionality.' if parser is None else 'Server is running with full functionality.'
    })

@app.after_request
def after_request(response):
    """Add CORS headers to all responses."""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/search_outfit', methods=['POST'])
def search_outfit():
    """
    Search for outfits based on a natural language prompt.
    
    Expected JSON payload:
    {
        "prompt": "old money summer vibe with deep autumn colors",
        "top_results_per_item": 3,
        "sort_by_price": true,
        "price_order": "asc"
    }
    
    Returns:
    {
        "success": true,
        "outfit_description": "Description of the envisioned outfit",
        "outfits": [
            {
                "outfit_id": 1,
                "items": [
                    {
                        "clothing_type": "shirts",
                        "name": "Product Name",
                        "price": "499,00 kr",
                        "url": "https://...",
                        "image_url": "https://..."
                    }
                ]
            }
        ],
        "total_outfits": 1,
        "total_products": 3
    }
    """
    
    # Log the incoming request
    logger.info("=" * 60)
    logger.info("🎯 NEW OUTFIT SEARCH REQUEST")
    logger.info("=" * 60)
    
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            logger.error("❌ No JSON data provided")
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        prompt = data.get('prompt')
        if not prompt:
            logger.error("❌ No prompt provided")
            return jsonify({
                'success': False,
                'error': 'No prompt provided'
            }), 400
        
        # Get optional parameters
        top_results_per_item = data.get('top_results_per_item', 1)  # Changed default to 1 for distinct outfits
        sort_by_price = data.get('sort_by_price', True)
        price_order = data.get('price_order', 'asc')
        
        logger.info(f"📝 Prompt: '{prompt}'")
        logger.info(f"🔍 Top results per item: {top_results_per_item}")
        logger.info(f"💰 Sort by price: {sort_by_price}")
        logger.info(f"📊 Price order: {price_order}")
        
        # Check if parser is ready
        if not parser:
            logger.error("❌ OutfitPromptParser not initialized")
            return jsonify({
                'success': False,
                'error': 'Server not ready. Please try again later.'
            }), 503
        
        # Step 1: Parse the prompt with AI
        logger.info("\n🤖 STEP 1: Parsing prompt with AI...")
        outfit_response = parser.parse_outfit_prompt(prompt)
        
        logger.info(f"✅ AI generated outfit description:")
        logger.info(f"   {outfit_response['outfit_description']}")
        
        logger.info(f"\n✅ Generated {len(outfit_response['outfit_variations'])} outfit variations:")
        for i, variation in enumerate(outfit_response['outfit_variations'], 1):
            logger.info(f"   {i}. {variation['variation_name']} - {variation['variation_description']}")
            for j, item in enumerate(variation['outfit_items'], 1):
                logger.info(f"      {j}. {item['clothing_type']}")
                if 'color' in item:
                    logger.info(f"         🎨 Color: {item['color']}")
                if 'filters' in item and item['filters']:
                    logger.info(f"         🔍 Filters: {item['filters']}")
        
        # Step 2: Search for products using the parsed outfit variations
        logger.info("\n🔍 STEP 2: Searching for products...")
        
        # Search for each outfit variation
        all_results = {}
        
        for variation in outfit_response['outfit_variations']:
            variation_name = variation['variation_name']
            logger.info(f"\n🔍 Searching for variation: {variation_name}")
            
            # Search for this variation's items
            variation_results = search_function.search_outfit(
                variation['outfit_items'],
                top_results_per_item=top_results_per_item,
                sort_by_price=sort_by_price,
                price_order=price_order
            )
            
            # Store results with variation name as key
            all_results[variation_name] = {
                'variation_description': variation['variation_description'],
                'products': variation_results
            }
        
        # Step 3: Structure the response
        logger.info("\n📦 STEP 3: Structuring response...")
        
        # Create outfits from each variation
        outfits = []
        outfit_id = 1
        total_products = 0
        
        for variation_name, variation_data in all_results.items():
            variation_description = variation_data['variation_description']
            products_by_category = variation_data['products']
            
            logger.info(f"\n👕 Processing variation: {variation_name}")
            logger.info(f"   Description: {variation_description}")
            
            # Get all clothing types that have results for this variation
            clothing_types_with_results = [ct for ct, products in products_by_category.items() if products]
            
            if not clothing_types_with_results:
                logger.warning(f"⚠️ No products found for variation: {variation_name}")
                continue
            
            # Create one outfit from this variation (taking the best item from each category)
            outfit_items = []
            
            for clothing_type in clothing_types_with_results:
                if products_by_category[clothing_type]:  # Check if there are products
                    product = products_by_category[clothing_type][0]  # Take the best item
                    outfit_items.append({
                        'clothing_type': clothing_type,
                        'name': product['name'],
                        'price': product['price'],
                        'url': product.get('original_url', ''),
                        'image_url': product.get('image_url', ''),
                        'secondary_image_url': product.get('secondary_image_url', '')
                    })
                    total_products += 1
            
            if outfit_items:  # Only add outfit if it has items
                outfits.append({
                    'outfit_id': outfit_id,
                    'variation_name': variation_name,
                    'variation_description': variation_description,
                    'items': outfit_items
                })
                outfit_id += 1
        
        total_outfits = len(outfits)
        
        if total_outfits == 0:
            logger.warning("⚠️ No products found for any variation")
            return jsonify({
                'success': True,
                'outfit_description': outfit_response['outfit_description'],
                'outfits': [],
                'total_outfits': 0,
                'total_products': 0,
                'message': 'No products found matching your criteria'
            })
        
        logger.info(f"✅ Created {total_outfits} distinct outfits with {total_products} total products")
        
        # Log each outfit for debugging
        for i, outfit in enumerate(outfits, 1):
            logger.info(f"\n👕 Outfit {i} ({outfit['variation_name']}):")
            logger.info(f"   Description: {outfit['variation_description']}")
            for item in outfit['items']:
                logger.info(f"   • {item['clothing_type']}: {item['name']} - {item['price']}")
        
        # Return the response
        response_data = {
            'success': True,
            'outfit_description': outfit_response['outfit_description'],
            'outfits': outfits,
            'total_outfits': total_outfits,
            'total_products': total_products,
            'search_metadata': {
                'prompt': prompt,
                'top_results_per_item': top_results_per_item,
                'sort_by_price': sort_by_price,
                'price_order': price_order,
                'variations_searched': list(all_results.keys())
            }
        }
        
        logger.info(f"\n✅ SUCCESS: Returning {total_outfits} outfits")
        logger.info("=" * 60)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.info("=" * 60)
        
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/parse_prompt', methods=['POST'])
def parse_prompt_only():
    """
    Parse a prompt without searching for products (for testing/debugging).
    
    Expected JSON payload:
    {
        "prompt": "old money summer vibe with deep autumn colors"
    }
    """
    
    logger.info("=" * 60)
    logger.info("🧠 PROMPT PARSING REQUEST")
    logger.info("=" * 60)
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'No prompt provided'
            }), 400
        
        logger.info(f"📝 Parsing prompt: '{prompt}'")
        
        if not parser:
            return jsonify({
                'success': False,
                'error': 'Server not ready. Please try again later.'
            }), 503
        
        # Parse the prompt
        outfit_response = parser.parse_outfit_prompt(prompt)
        
        logger.info(f"✅ Parsed successfully")
        logger.info("=" * 60)
        
        return jsonify({
            'success': True,
            'outfit_description': outfit_response['outfit_description'],
            'outfit_variations': outfit_response['outfit_variations']
        })
        
    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.info("=" * 60)
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/search_outfit_dummy', methods=['POST'])
def search_outfit_dummy():
    """
    Search for outfits based on a natural language prompt - returns dummy data for testing.
    This endpoint returns pre-captured data without running the LLM.
    
    Expected JSON payload:
    {
        "prompt": "old money summer vibe with deep autumn colors",
        "top_results_per_item": 3,
        "sort_by_price": true,
        "price_order": "asc"
    }
    
    Returns:
    {
        "success": true,
        "outfit_description": "Description of the envisioned outfit",
        "outfits": [
            {
                "outfit_id": 1,
                "variation_name": "Resort Elegance",
                "variation_description": "An airy summer look...",
                "items": [
                    {
                        "clothing_type": "shirts",
                        "name": "Product Name",
                        "price": "499,00 kr",
                        "url": "https://...",
                        "image_url": "https://..."
                    }
                ]
            }
        ],
        "total_outfits": 3,
        "total_products": 8
    }
    """
    
    # Log the incoming request
    logger.info("=" * 60)
    logger.info("🎯 DUMMY OUTFIT SEARCH REQUEST")
    logger.info("=" * 60)
    
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            logger.error("❌ No JSON data provided")
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        prompt = data.get('prompt')
        if not prompt:
            logger.error("❌ No prompt provided")
            return jsonify({
                'success': False,
                'error': 'No prompt provided'
            }), 400
        
        # Get optional parameters
        top_results_per_item = data.get('top_results_per_item', 2)
        sort_by_price = data.get('sort_by_price', True)
        price_order = data.get('price_order', 'asc')
        
        logger.info(f"📝 Prompt: '{prompt}'")
        logger.info(f"🔍 Top results per item: {top_results_per_item}")
        logger.info(f"💰 Sort by price: {sort_by_price}")
        logger.info(f"📊 Price order: {price_order}")
        
        # Return dummy data (pre-captured from a real search)
        dummy_response = {
            "success": True,
            "outfit_description": "Three sophisticated summer interpretations of the old money aesthetic in deep autumn hues, each offering a unique balance of timeless refinement, contemporary polish, and bold statement-making style.",
            "outfits": [
                {
                    "outfit_id": 1,
                    "variation_name": "Resort Elegance",
                    "variation_description": "An airy summer look featuring a short-sleeve linen shirt in rich brown paired with tailored beige linen chino shorts—effortlessly relaxed yet polished.",
                    "items": [
                        {
                            "clothing_type": "shirts",
                            "name": "120% Lino - SHORT SLEEVE MEN RELAXED FIT SHIRT - Skjorta - almond",
                            "price": "1 048,00 kr",
                            "url": "https://www.zalando.se/120-lino-short-sleeve-men-relaxed-fit-shirt-skjorta-almond-l1922d01v-o11.html",
                            "image_url": "https://img01.ztat.net/article/spp-media-p1/3b63fa788765454e91b900d4ceeb148f/824fc7c9e7384548ac941aed8c42189d.jpg?imwidth=300",
                            "secondary_image_url": None
                        },
                        {
                            "clothing_type": "shorts",
                            "name": "Massimo Dutti - Chinos - beige",
                            "price": "650,00 kr",
                            "url": "https://www.zalando.se/massimo-dutti-kostymbyxor-beige-m3i22e0me-b11.html",
                            "image_url": "https://img01.ztat.net/article/spp-media-p1/01fb0d3021014e7985c67848f32cf19f/e6179391c05e4ac5b6024646c08013a0.jpg?imwidth=300",
                            "secondary_image_url": None
                        }
                    ]
                },
                {
                    "outfit_id": 2,
                    "variation_name": "Modern Aristocrat",
                    "variation_description": "A sophisticated layered outfit with a crisp white oxford shirt, a lightweight brown cashmere knit, and olive linen trousers for a polished country-club vibe.",
                    "items": [
                        {
                            "clothing_type": "shirts",
                            "name": "Pier One - SHORT SLEEVE OXFORD - Skjorta - white",
                            "price": "309,00 kr",
                            "url": "https://www.zalando.se/pier-one-skjorta-white-pi922d0g0-a11.html",
                            "image_url": "https://img01.ztat.net/article/spp-media-p1/994ce5a5776049439fc90f91e9376815/ef7fd3f82cac4d9ca2f03b050a4cb62c.jpg?imwidth=300",
                            "secondary_image_url": None
                        },
                        {
                            "clothing_type": "knitwear",
                            "name": "Massimo Dutti - Stickad tröja - light brown",
                            "price": "1 000,00 kr",
                            "url": "https://www.zalando.se/massimo-dutti-stickad-troeja-light-brown-m3i22q0ix-o11.html",
                            "image_url": "https://img01.ztat.net/article/spp-media-p1/b77924d1f64c4340adc4c298dc42ba73/cc13d588c01a4d52acf294998375f8cf.jpg?imwidth=300",
                            "secondary_image_url": None
                        },
                        {
                            "clothing_type": "pants",
                            "name": "Next - REGULAR FIT SIGNATURE ELASTICATED WAIST DRAWSTRING - Tygbyxor - neutral",
                            "price": "724,00 kr",
                            "url": "https://www.zalando.se/next-tygbyxor-neutral-nx322e1bw-n11.html",
                            "image_url": "https://img01.ztat.net/article/spp-media-p1/5e58171bd2ed48adb70e0da5285196fc/8b27b8742a0344cd94be3b6e07382fea.jpg?imwidth=300",
                            "secondary_image_url": None
                        }
                    ]
                },
                {
                    "outfit_id": 3,
                    "variation_name": "Preppy Layered",
                    "variation_description": "A modern preppy twist with an emerald cotton tee under a burnt orange cable-knit sweater, paired with crisp beige linen pants for a crisp autumnal contrast.",
                    "items": [
                        {
                            "clothing_type": "t_shirts",
                            "name": "Massimo Dutti - SHORT SLEEVE WITH PLACKET - Piké - dark green",
                            "price": "200,00 kr",
                            "url": "https://www.zalando.se/massimo-dutti-short-sleeve-with-placket-pike-dark-green-m3i22o09j-m11.html",
                            "image_url": "https://img01.ztat.net/article/spp-media-p1/a10467beb98c40ecaa0c504c105703a2/2328882d48c141d396a19e4ced7abf78.jpg?imwidth=300",
                            "secondary_image_url": None
                        },
                        {
                            "clothing_type": "knitwear",
                            "name": "Solid - SDVal - Skjorta - arabian spice",
                            "price": "424,00 kr",
                            "url": "https://www.zalando.se/solid-sdval-stripe-skjorta-arabian-spice-so422d0a8-h11.html",
                            "image_url": "https://img01.ztat.net/article/spp-media-p1/c32da8631b6c4dafb64fc8ccca48c002/08b053837fe6403a883a8f733fa4019c.jpg?imwidth=300",
                            "secondary_image_url": None
                        },
                        {
                            "clothing_type": "pants",
                            "name": "Massimo Dutti - Chinos - beige",
                            "price": "650,00 kr",
                            "url": "https://www.zalando.se/massimo-dutti-kostymbyxor-beige-m3i22e0me-b11.html",
                            "image_url": "https://img01.ztat.net/article/spp-media-p1/01fb0d3021014e7985c67848f32cf19f/e6179391c05e4ac5b6024646c08013a0.jpg?imwidth=300",
                            "secondary_image_url": None
                        }
                    ]
                }
            ],
            "total_outfits": 3,
            "total_products": 8,
            "search_metadata": {
                "prompt": prompt,
                "top_results_per_item": top_results_per_item,
                "sort_by_price": sort_by_price,
                "price_order": price_order,
                "variations_searched": ["Resort Elegance", "Modern Aristocrat", "Preppy Layered"],
                "note": "This is dummy data for testing purposes"
            }
        }
        
        logger.info(f"✅ DUMMY SUCCESS: Returning {dummy_response['total_outfits']} outfits")
        logger.info("=" * 60)
        
        return jsonify(dummy_response)
        
    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.info("=" * 60)
        
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Outfit Search Flask Server...")
    logger.info("📋 Available endpoints:")
    logger.info("   GET  /health - Health check")
    logger.info("   POST /search_outfit - Search for outfits")
    logger.info("   POST /parse_prompt - Parse prompt only")
    logger.info("   POST /search_outfit_dummy - Search for outfits - returns dummy data")
    logger.info("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5003,
        debug=True,
        threaded=True
    )
