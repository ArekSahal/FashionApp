#!/usr/bin/env python3
"""
Flask server for AI-powered outfit search.
Takes natural language outfit descriptions and returns structured outfit recommendations.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from outfit_prompt_parser import OutfitPromptParser
from config import Config
import logging
from datetime import datetime
import traceback
import os
import json
import math

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/outfit_server.log')
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

def sanitize_for_json(obj):
    """
    Recursively sanitize data to ensure all floats are valid JSON (no Infinity/NaN).
    Replace such values with None.
    """
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    else:
        return obj

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
        "top_results_per_item": 3,  # optional
        "sort_by_price": true,      # optional
        "price_order": "asc"       # optional
    }
    """
    logger.info("=" * 60)
    logger.info("🧠 OUTFIT SEARCH REQUEST")
    logger.info("=" * 60)
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({'success': False, 'error': 'No prompt provided'}), 400
        top_results_per_item = data.get('top_results_per_item', 1)
        sort_by_price = data.get('sort_by_price', True)
        price_order = data.get('price_order', 'asc')
        
        logger.info(f"📝 Searching outfits for prompt: '{prompt}'")
        if not parser:
            return jsonify({'success': False, 'error': 'Server not ready. Please try again later.'}), 503
        # Perform the outfit search
        search_results = parser.search_outfit_from_prompt(
            prompt
        )
        logger.info(f"🔎 Search results: {search_results}")
        logger.info(f"✅ Outfit search completed")
        logger.info("=" * 60)

        # --- Write search results to file for debugging ---
        try:
            with open('logs/last_search_outfit.json', 'w', encoding='utf-8') as f:
                json.dump(search_results, f, ensure_ascii=False, indent=2)
        except Exception as file_err:
            logger.error(f"Failed to write search results to file: {file_err}")
        # --- Sanitize before returning ---
        return jsonify(sanitize_for_json(search_results))
    except Exception as e:
        logger.error(f"❌ ERROR: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.info("=" * 60)
        return jsonify(sanitize_for_json({'success': False, 'error': str(e)})), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify(sanitize_for_json({
        'success': False,
        'error': 'Endpoint not found'
    })), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify(sanitize_for_json({
        'success': False,
        'error': 'Internal server error'
    })), 500

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
