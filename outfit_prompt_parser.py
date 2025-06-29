import openai
import json
from typing import List, Dict, Any, Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_collection'))
import importlib.util

from search_function import (
    extract_price,
    calculate_product_relevance_score,
    search_database_products,
    search_products_by_text
)
from config import Config
# Import constants from zalando_scraper
from data_collection.zalando_scraper import CLOTHING_TYPES, COLORS, MATERIALS, validate_material

# Load allowed tags from data_collection/allowed_tags.py
spec = importlib.util.spec_from_file_location("allowed_tags", os.path.join(os.path.dirname(__file__), "data_collection", "allowed_tags.py"))
allowed_tags_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(allowed_tags_module)
ALLOWED_TAGS = set(allowed_tags_module.ALLOWED_TAGS)

# Stub functions for inventory summary and detailed inventory
# (Replace with real implementations if needed)
def get_database_inventory_summary():
    return {'clothing_types': list(CLOTHING_TYPES.keys()), 'colors': list(COLORS.keys())}

def get_available_materials_from_database():
    return {'building_blocks': MATERIALS}

def get_detailed_inventory_by_clothing_type():
    return {}

# Add clothing category mapping
CLOTHING_CATEGORY_MAP = {
    "t-shirt": "top",
    "shirt": "top",
    "blouse": "top",
    "polo": "top",
    "tank-top": "top",
    "sweater": "sweater",
    "hoodie": "sweater",
    "cardigan": "sweater",
    "jacket": "outerwear",
    "coat": "outerwear",
    "blazer": "outerwear",
    "vest": "outerwear",
    "suit": "outerwear",
    "jeans": "bottom",
    "trousers": "bottom",
    "shorts": "bottom",
    "skirt": "bottom",
    "leggings": "bottom",
    "jumpsuit": "bottom",
    "romper": "bottom",
    "sweatpants": "bottom",
    "tracksuit": "bottom",
    "overalls": "bottom",
    "shoes": "footwear",
    "sneakers": "footwear",
    "boots": "footwear",
    "loafers": "footwear",
    "sandals": "footwear",
    "slippers": "footwear",
    "socks": "accessory",
    "scarf": "accessory",
    "cape": "accessory",
    "wrap": "accessory",
}

class OutfitPromptParser:
    """
    A class that uses OpenAI API to parse natural language outfit descriptions
    into structured search parameters for the outfit search function.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the parser with OpenAI API key.
        
        Args:
            api_key (str): OpenAI API key
        """
        self.client = openai.OpenAI(api_key=api_key)
        
        # Get available data from database
        self.inventory_summary = get_database_inventory_summary()
        
        # Available clothing types, colors, and materials from database
        self.clothing_types = self.inventory_summary.get('clothing_types', [])
        self.colors = self.inventory_summary.get('colors', [])
        self.materials_data = get_available_materials_from_database()
        self.available_materials = self.materials_data.get('building_blocks', [])
        
        # Get detailed inventory by clothing type
        self.detailed_inventory = get_detailed_inventory_by_clothing_type()
        
    def parse_outfit_prompt(self, prompt: str, max_items_per_category: int = 5, max_retries: int = 3) -> dict:
        """
        Generate 3 outfit ideas, each with multiple clothing pieces (organized by clothing type),
        extract tags for each piece, and prepare for tag-based search.
        Also returns a top-level 'outfit_description' summarizing all ideas for API compatibility.
        Also returns 'outfit_variations' in the old format for server compatibility.
        """
        self.inventory_summary = get_database_inventory_summary()
        self.clothing_types = self.inventory_summary.get('clothing_types', [])
        self.colors = self.inventory_summary.get('colors', [])
        self.materials_data = get_available_materials_from_database()
        self.available_materials = self.materials_data.get('building_blocks', [])
        self.detailed_inventory = get_detailed_inventory_by_clothing_type()
        detailed_inventory_text = self._format_detailed_inventory_for_ai()

        def validate_outfit(outfit):
            clothing_types = []
            for piece in outfit.get('clothing_pieces', []):
                ct = piece.get('clothing_type')
                if isinstance(ct, list):
                    clothing_types.extend([c.lower() for c in ct])
                elif isinstance(ct, str):
                    clothing_types.append(ct.lower())
            clothing_types_set = set(clothing_types)
            # Map clothing types to categories
            categories = [CLOTHING_CATEGORY_MAP.get(ct, ct) for ct in clothing_types]
            from collections import Counter
            cat_counter = Counter(categories)
            has_more_than_one_per_category = any(count > 1 for count in cat_counter.values())
            # Check for at least one top and one bottom (shoes/socks not required)
            TOPS = {k for k, v in CLOTHING_CATEGORY_MAP.items() if v == "top"}
            BOTTOMS = {k for k, v in CLOTHING_CATEGORY_MAP.items() if v == "bottom"}
            has_top = any(ct in TOPS for ct in clothing_types_set)
            has_bottom = any(ct in BOTTOMS for ct in clothing_types_set)
            if not (has_top and has_bottom):
                return False, "Outfit must include at least one top and one bottom. Shoes and socks are optional."
            if has_more_than_one_per_category:
                return False, "Outfit contains more than one item from the same clothing category. Only one of each category is allowed (e.g., only one top, one bottom, one sweater, etc.)."
            return True, ""

        for attempt in range(max_retries):
            try:
                system_prompt = self._create_structured_outfit_prompt(detailed_inventory_text, max_items_per_category, attempt)
                response = self.client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=1,
                    max_completion_tokens=20000
                )
                content = response.choices[0].message.content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                elif content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                parsed_response = json.loads(content)
                # Validate structure
                if 'outfit_ideas' not in parsed_response or not isinstance(parsed_response['outfit_ideas'], list):
                    raise ValueError("LLM response must contain 'outfit_ideas' as a list")
                if len(parsed_response['outfit_ideas']) != 3:
                    raise ValueError("LLM must return exactly 3 outfit ideas")
                # For each idea, for each clothing piece, extract tags
                for idea in parsed_response['outfit_ideas']:
                    for piece in idea.get('clothing_pieces', []):
                        piece['tags'] = self._extract_tags_from_description(piece.get('description', ''))
                # Add a top-level outfit_description for API compatibility
                if 'outfit_description' not in parsed_response:
                    summary = ' '.join([idea['description'] for idea in parsed_response['outfit_ideas'] if 'description' in idea])
                    parsed_response['outfit_description'] = summary
                # Add 'outfit_variations' for server compatibility (old format, no items)
                if 'outfit_variations' not in parsed_response:
                    parsed_response['outfit_variations'] = [
                        {
                            'variation_name': idea.get('name', f'Variation {i+1}'),
                            'variation_description': idea.get('description', ''),
                            'outfit_items': []
                        } for i, idea in enumerate(parsed_response['outfit_ideas'])
                    ]
                # Validate each outfit
                for idx, idea in enumerate(parsed_response['outfit_ideas']):
                    valid, reason = validate_outfit(idea)
                    if not valid:
                        raise ValueError(f"Outfit idea {idx+1} failed validation: {reason}")
                return parsed_response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to parse outfit prompt after {max_retries} attempts: {e}")
                continue
        raise ValueError(f"Failed to parse outfit prompt after {max_retries} attempts")

    def _create_structured_outfit_prompt(self, detailed_inventory_text: str, max_items_per_category: int, attempt: int = 0) -> str:
        """
        System prompt for generating 3 creative outfit ideas, each with multiple clothing pieces (organized by clothing type).
        """
        clothing_types_list = [
            "t-shirt", "shirt", "blouse", "dress", "skirt", "jeans", "trousers", "shorts", "jacket", "coat", "sweater",
            "hoodie", "suit", "blazer", "vest", "tank-top", "leggings", "jumpsuit", "romper", "cardigan", "polo",
            "sweatpants", "tracksuit", "bodysuit", "overalls", "cape", "wrap", "scarf"
        ]
        # Add clothing categories and their types for the prompt
        clothing_categories = {
            "top": ["t-shirt", "shirt", "blouse", "polo", "tank-top"],
            "sweater": ["sweater", "hoodie", "cardigan"],
            "outerwear": ["jacket", "coat", "blazer", "vest", "suit"],
            "bottom": ["jeans", "trousers", "shorts", "skirt", "leggings", "jumpsuit", "romper", "sweatpants", "tracksuit", "overalls"],
            "footwear": ["shoes", "sneakers", "boots", "loafers", "sandals", "slippers"],
            "accessory": ["socks", "scarf", "cape", "wrap"]
        }
        category_text = "\n".join([
            f"- {cat.capitalize()}: {', '.join(types)}" for cat, types in clothing_categories.items()
        ])
        system_prompt = f"""You are an expert fashion stylist and outfit planner. Your task is to generate 3 creative and distinct outfit ideas based on the user's prompt. Each idea should have a name, a high-level description, and a breakdown into multiple clothing pieces (such as shirt, pants, etc.).\n\nALL OUTFIT IDEAS AND CLOTHING PIECES SHOULD BE FOR MEN'S CLOTHING ONLY.\n\n**IMPORTANT: Each outfit must be a complete, wearable look for a man.**\n\n**REQUIRED: Each outfit MUST include AT LEAST:**\n- One top (e.g., shirt, t-shirt, sweater, hoodie, etc.)\n- One bottom (e.g., jeans, trousers, shorts, etc.)\n\nThese are REQUIRED and cannot be omitted. Shoes/footwear and socks are optional and NOT required.\n\n**STRICT CATEGORY RULES:**\n- Each outfit may include AT MOST ONE item from each clothing category. For example, you may include a \"shirt\" OR a \"t-shirt\" (both are \"tops\"), but NOT both. You may include a \"t-shirt\" and a \"sweater\" (since \"sweater\" is a different category). Do NOT include multiple items from the same category in a single outfit.\n- You may include outerwear (e.g., jacket, coat) and accessories (e.g., scarf), but these are optional and cannot replace the required categories above.\n- Do NOT generate outfits that consist only of tops, only bottoms, or only accessories.\n- Do NOT generate outfits with more than one of any clothing category.\n- All pieces together must form a full, wearable outfit.\n\n**Clothing Categories:**\n{category_text}\n\n**Checklist for each outfit (ALL must be satisfied):**\n- [ ] Includes at least one top (REQUIRED)\n- [ ] Includes at least one bottom (REQUIRED)\n- [ ] No more than one item from any clothing category\n- [ ] All pieces together form a full, wearable outfit\n\nFor each clothing piece, you MUST provide its clothing_type (from the CLOTHING TYPES list below). The clothing_type can be either a single string (e.g., \"shirt\") or a list of strings (e.g., [\"shirt\", \"t-shirt\"]) if multiple types are acceptable. Each outfit must include at least one clothing piece with a clothing_type. Use the available inventory and be as descriptive as possible.\n\nAVAILABLE INVENTORY:\n{detailed_inventory_text}\n\nCLOTHING TYPES (use only these for clothing_type): {', '.join(clothing_types_list)}\nAVAILABLE COLORS: {', '.join(self.colors)}\nAVAILABLE MATERIAL BUILDING BLOCKS: {', '.join(self.available_materials)}\n\nTASK:\n1. Generate 3 creative and distinct outfit ideas based on the user's prompt.\n2. For each idea, provide:\n   - a name\n   - a high-level description\n   - a list of clothing pieces, each with:\n     - clothing_type (from the CLOTHING TYPES list above; required for every piece; can be a string or a list of strings)\n     - name\n     - detailed description\n3. Be as descriptive as possible using the available inventory.\n4. Do NOT return any search parameters or JSON for search, just ideas and descriptions.\n\nOUTPUT FORMAT:\n{{\n  \"outfit_ideas\": [\n    {{\n      \"name\": \"Name of the outfit idea\",\n      \"description\": \"High-level description of the outfit idea\",\n      \"clothing_pieces\": [\n        {{\n          \"clothing_type\": \"Type of clothing (from CLOTHING TYPES list, e.g., shirt, pants)\",\n          \"name\": \"Name of the piece\",\n          \"description\": \"Detailed description of the piece\"\n        }},\n        {{\n          \"clothing_type\": [\"shirt\", \"t-shirt\"],\n          \"name\": \"Name of the piece\",\n          \"description\": \"Detailed description of the piece\"\n        }},\n        ... (multiple pieces)\n      ]\n    }},\n    ... (total 3 ideas)\n  ]\n}}\n"""
        if attempt > 0:
            system_prompt += f"\n\nRETRY ATTEMPT {attempt + 1}: Be more creative and ensure 3 distinct ideas, each with multiple clothing pieces. Each piece must have a clothing_type from the CLOTHING TYPES list, as a string or a list. Each outfit must be a complete, wearable look as described above, and must not have more than one item from any clothing category."
        return system_prompt

    def _extract_tags_from_description(self, description: str) -> list:
        """
        Extract as many relevant tags as possible from the description using ALLOWED_TAGS.
        """
        desc = description.lower()
        tags = [tag for tag in ALLOWED_TAGS if tag in desc]
        return tags

    def _format_detailed_inventory_for_ai(self) -> str:
        """
        Format the detailed inventory information for the AI model.
        
        Returns:
            str: Formatted inventory information
        """
        if not self.detailed_inventory:
            return "No detailed inventory available."
        
        formatted_lines = []
        for clothing_type, data in self.detailed_inventory.items():
            formatted_lines.append(f"\n{clothing_type.upper()}:")
            formatted_lines.append(f"  Products: {data['product_count']}")
            formatted_lines.append(f"  Materials: {', '.join(data['materials'])}")
            formatted_lines.append(f"  Colors: {', '.join(data['colors'])}")
            
            if data['material_color_combinations']:
                formatted_lines.append("  Valid Material-Color Combinations:")
                for material, colors in data['material_color_combinations'].items():
                    if colors:  # Only show materials that have colors
                        formatted_lines.append(f"    {material}: {', '.join(colors)}")
        
        return "\n".join(formatted_lines)

    def search_outfit_from_prompt(self, prompt: str, top_results_per_item: int = 3, 
                                 sort_by_price: bool = True, price_order: str = 'asc') -> dict:
        """
        Parse the prompt, generate outfit ideas (each with multiple clothing pieces), and search for matching products for each piece.
        Returns a dict with outfit ideas, each containing clothing pieces, tags, and matching products.
        """
        # Parse the prompt to get outfit ideas and tags per piece
        parsed = self.parse_outfit_prompt(prompt)
        outfit_ideas = parsed.get('outfit_ideas', [])
        results = []
        for idea in outfit_ideas:
            idea_result = {
                'idea_name': idea.get('name'),
                'idea_description': idea.get('description'),
                'clothing_pieces': []
            }
            for piece in idea.get('clothing_pieces', []):
                tags = piece.get('tags', [])
                clothing_type = piece.get('clothing_type')
                filters = {}
                # Handle clothing_type as string or list
                if clothing_type:
                    if isinstance(clothing_type, list):
                        filters['clothing_type'] = clothing_type
                    else:
                        filters['clothing_type'] = clothing_type
                # Debug print
                print(f"\n[DEBUG] Searching for piece: {piece.get('name')}")
                print(f"[DEBUG]   clothing_type: {clothing_type}")
                print(f"[DEBUG]   filters: {filters}")
                print(f"[DEBUG]   tags: {tags}")
                products = search_database_products(
                    target_tags=tags,
                    max_items=top_results_per_item,
                    sort_by_price=sort_by_price,
                    price_order=price_order,
                    use_relevance_scoring=True,
                    filters=filters
                )
                idea_result['clothing_pieces'].append({
                    'clothing_type': clothing_type,
                    'piece_name': piece.get('name'),
                    'piece_description': piece.get('description'),
                    'tags': tags,
                    'products': products
                })
            results.append(idea_result)
        return {
            'prompt': prompt,
            'outfit_ideas': results
        }

# Remove test_outfit_parser and any other test or dummy functions related to outfit search 