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
    load_all_products_from_supabase
)
from config import Config

# Load allowed tags from data_collection/allowed_tags.py
spec = importlib.util.spec_from_file_location("allowed_tags", os.path.join(os.path.dirname(__file__), "data_collection", "allowed_tags.py"))
allowed_tags_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(allowed_tags_module)
ALLOWED_TAGS = set(allowed_tags_module.DESCRIPTIVE_TAGS + allowed_tags_module.CLOTHING_TYPES + allowed_tags_module.COLORS)
DESCRIPTIVE_TAGS = allowed_tags_module.DESCRIPTIVE_TAGS
CLOTHING_TYPES = allowed_tags_module.CLOTHING_TYPES
COLORS = allowed_tags_module.COLORS

# Add at the top, after imports
KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.txt")
def load_knowledge_base():
    try:
        with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""

class OutfitPromptParser:
    """
    A class that uses OpenAI API to parse natural language outfit descriptions
    into structured search parameters for the outfit search function.
    """
    
    # System prompt template for generating outfit ideas
    SYSTEM_PROMPT_TEMPLATE = """
    You are an expert fashion stylist and outfit planner. Your task is to generate 3 creative and distinct outfit ideas 
    based on the user's prompt. Each idea should have a name, a high-level description, and a breakdown into multiple 
    clothing pieces (such as shirt, pants, etc.).

    {knowledge_base}

    ALL OUTFIT IDEAS AND CLOTHING PIECES SHOULD BE FOR MEN'S CLOTHING ONLY.

    **IMPORTANT: Each outfit must be a complete, wearable look for a man.**

    **REQUIRED: Each outfit MUST include AT LEAST:**
    - One top (e.g., shirt, t-shirt, sweater, hoodie, etc.)
    - One bottom (e.g., jeans, trousers, shorts, etc.)
    These are REQUIRED and cannot be omitted.
    Shoes/footwear and socks are optional and NOT required.
    - All pieces together must form a full, wearable outfit.

    TASK:
    1. Generate 3 creative and distinct outfit ideas based on the user's prompt.
    2. For each idea, provide:
       - a name
       - a high-level description
       - a list of clothing pieces, each with:
        - clothing_type (from the CLOTHING TYPES list below; required for every piece; can be a string or a list of strings)
        - name
        - detailed description
        - tags (list of tags from the DESCRIPTIVE TAGS, CLOTHING TYPES, and COLORS lists below)
    3. Be as descriptive as possible using the available inventory.

    ALLOWED TAGS FOR GENERATION:

    DESCRIPTIVE TAGS:
    {descriptive_tags}

    CLOTHING TYPES:
    {clothing_types}

    COLORS:
    {colors}

    OUTPUT FORMAT:
    {{
      "outfit_ideas": [
          {{
               "name": "Name of the outfit idea",
               "description": "High-level description of the outfit idea",
               "clothing_pieces": [
                 {{
                   "clothing_type": "shorts",
                   "name": "Name of the piece", 
                   "color": ["red", "pink"],
                   "description": "Detailed description of the piece",
                   "tags": ["tag1", "tag2", "tag3", ...]
                 }},
                 {{
                   "clothing_type": ["shirt", "t-shirt"],
                   "name": "Name of the piece",
                   "color": ["blue", "teal"],
                   "description": "Detailed description of the piece",
                   "tags": ["tag1", "tag2", "tag3",...]
                 }},
                 ... (multiple pieces)
               ]
          }},
          ... (total 3 ideas)
      ]
    }}
    """

    def __init__(self, api_key: str, knowledge_base: Optional[str] = None):
        """
        Initialize the parser with OpenAI API key and optional knowledge base.
        Args:
            api_key (str): OpenAI API key
            knowledge_base (str, optional): Additional knowledge base text to inject into the prompt
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.knowledge_base = knowledge_base if knowledge_base is not None else load_knowledge_base()
        
        
    
        
    def parse_outfit_prompt(self, prompt: str, max_items_per_category: int = 1, max_retries: int = 3) -> dict:
        """
        Generate 3 outfit ideas, an outfit should contain at least one top and one bottom and no more than one of any category, expect the person to wear everything that you suggest in the outfit.
        Extract tags for each piece, and prepare for tag-based search.
        Also returns a top-level 'outfit_description' summarizing all ideas for API compatibility.
        Also returns 'outfit_variations' in the old format for server compatibility.
        """



        for attempt in range(max_retries):
            try:
                system_prompt = self._create_structured_outfit_prompt( max_items_per_category, attempt)
                response = self.client.chat.completions.create(
                    model="gpt-4.1-nano",
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
                return parsed_response
            except Exception as e:
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to parse outfit prompt after {max_retries} attempts: {e}")
                continue
        raise ValueError(f"Failed to parse outfit prompt after {max_retries} attempts")

    def _create_structured_outfit_prompt(self, max_items_per_category: int, attempt: int = 0) -> str:
        """
        System prompt for generating 3 creative outfit ideas, each with multiple clothing pieces (organized by clothing type).
        """
        descriptive_tags = ', '.join(DESCRIPTIVE_TAGS)
        clothing_types = ', '.join(CLOTHING_TYPES)
        colors = ', '.join(COLORS)
        prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
            knowledge_base=self.knowledge_base,
            descriptive_tags=descriptive_tags,
            clothing_types=clothing_types,
            colors=colors
        )
        if attempt > 0:
            prompt += f"\n\nRETRY ATTEMPT {attempt + 1}: Be more creative and ensure 3 distinct ideas. Each piece must have a clothing_type from the CLOTHING TYPES list, as a string or a list. Each outfit must be a complete, wearable look as described above, and must not have more than one item from any clothing category."
        return prompt

    def _extract_tags_from_description(self, description: str) -> list:
        """
        Extract as many relevant tags as possible from the description using ALLOWED_TAGS.
        """
        desc = description.lower()
        tags = [tag for tag in ALLOWED_TAGS if tag in desc]
        return tags

    

    def search_outfit_from_prompt(self, prompt: str, top_results_per_item: int = 1, 
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
                print(f"[DEBUG]   color: {piece.get('color')}")
                products = search_database_products(
                    target_tags=tags,
                    max_items=top_results_per_item,
                    sort_by_price=sort_by_price,
                    price_order=price_order,
                    use_relevance_scoring=True,
                    clothing_type=clothing_type,
                    color=piece.get('color')
                )
                idea_result['clothing_pieces'].append({
                    'clothing_type': clothing_type,
                    'piece_name': piece.get('name'),
                    'piece_description': piece.get('description'),
                    'tags': tags,
                    'products': products,
                    'color': piece.get('color')
                })
            results.append(idea_result)
        return {
            'prompt': prompt,
            'outfit_ideas': results
        }

def pretty_print_search_results(results):
    print("\n=== OUTFIT SEARCH RESULTS ===")
    print(f"Prompt: {results.get('prompt', '')}\n")
    for idx, idea in enumerate(results.get('outfit_ideas', []), 1):
        print(f"--- Outfit Idea {idx}: {idea.get('idea_name', '')} ---")
        print(f"Description: {idea.get('idea_description', '')}")
        print("Clothing Pieces:")
        for piece in idea.get('clothing_pieces', []):
            print(f"  - Name: {piece.get('piece_name', '')}")
            print(f"    Type: {piece.get('clothing_type', '')}")
            print(f"    Description: {piece.get('piece_description', '')}")
            print(f"    Tags: {', '.join(piece.get('tags', []))}")
            print(f"    Color: {', '.join(piece.get('color', []))}")
            if piece.get('products'):
                print(f"    Products: {len(piece['products'])} found")
            else:
                print(f"    Products: None found")
        print()
    print("=== END OF RESULTS ===\n")

# Remove test_outfit_parser and any other test or dummy functions related to outfit search 

if __name__ == "__main__":
    parser = OutfitPromptParser(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = "sporty with a hoodie"
    results = parser.search_outfit_from_prompt(prompt)
    pretty_print_search_results(results)

def refresh_product_cache():
    load_all_products_from_supabase()