import openai
import json
from typing import List, Dict, Any, Optional
from search_function import (
    search_outfit, 
    CLOTHING_TYPES, 
    COLORS, 
    MATERIALS, 
    get_available_materials_from_database,
    get_available_clothing_types_from_database,
    get_available_colors_from_database,
    get_database_inventory_summary,
    get_detailed_inventory_by_clothing_type,
    get_available_combinations_for_clothing_type,
    validate_material_color_combination
)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import Config

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
        Parse a natural language outfit description into structured search parameters.
        
        Args:
            prompt (str): Natural language description (e.g., "old money summer vibe with deep autumn colors")
            max_items_per_category (int): Maximum items to search per clothing category
            max_retries (int): Maximum number of retries if validation fails
            
        Returns:
            dict: Dictionary containing:
                - outfit_description (str): Description of the envisioned outfit
                - outfit_items (list): List of outfit items with search parameters
        """
        
        # Get the latest data from database
        self.inventory_summary = get_database_inventory_summary()
        self.clothing_types = self.inventory_summary.get('clothing_types', [])
        self.colors = self.inventory_summary.get('colors', [])
        self.materials_data = get_available_materials_from_database()
        self.available_materials = self.materials_data.get('building_blocks', [])
        self.detailed_inventory = get_detailed_inventory_by_clothing_type()
        
        # Create detailed inventory information for the AI model
        detailed_inventory_text = self._format_detailed_inventory_for_ai()
        
        for attempt in range(max_retries):
            try:
                system_prompt = self._create_system_prompt(detailed_inventory_text, max_items_per_category, attempt)
                
                response = self.client.chat.completions.create(
                    model="o4-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=1,
                    max_completion_tokens=20000
                )
                
                # Extract the JSON response
                content = response.choices[0].message.content.strip()
                
                # Handle markdown code blocks if present
                if content.startswith('```json'):
                    content = content[7:]  # Remove ```json
                elif content.startswith('```'):
                    content = content[3:]   # Remove ```
                
                if content.endswith('```'):
                    content = content[:-3]  # Remove trailing ```
                
                content = content.strip()
                
                # Parse the JSON response
                parsed_response = json.loads(content)
                
                # Validate the response
                self._validate_outfit_items(parsed_response)
                
                return parsed_response
                
            except json.JSONDecodeError as e:
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to parse JSON response after {max_retries} attempts: {e}")
                continue
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to parse outfit prompt after {max_retries} attempts: {e}")
                continue
        
        raise ValueError(f"Failed to parse outfit prompt after {max_retries} attempts")

    def _create_system_prompt(self, detailed_inventory_text: str, max_items_per_category: int, attempt: int = 0) -> str:
        """
        Create the system prompt for the OpenAI API.
        
        Args:
            detailed_inventory_text (str): Formatted detailed inventory information
            max_items_per_category (int): Maximum items per category
            attempt (int): Current attempt number (for retry logic)
            
        Returns:
            str: System prompt for the AI model
        """
        
        # Base system prompt
        system_prompt = f"""You are an expert fashion stylist and outfit planner. Your task is to parse natural language outfit descriptions into structured search parameters.

AVAILABLE INVENTORY:
{detailed_inventory_text}

AVAILABLE CLOTHING TYPES: {', '.join(self.clothing_types)}
AVAILABLE COLORS: {', '.join(self.colors)}
AVAILABLE MATERIAL BUILDING BLOCKS: {', '.join(self.available_materials)}

TASK:
Parse the user's outfit description into a structured format that can be used to search for clothing items.

REQUIREMENTS:
1. Use ONLY clothing types from the available list: {', '.join(self.clothing_types)}
2. Use ONLY colors from the available list: {', '.join(self.colors)}
3. Use ONLY material building blocks from the available list: {', '.join(self.available_materials)}
4. Maximum {max_items_per_category} items per clothing category
5. Ensure all material-color combinations exist in the detailed inventory
6. Create multiple outfit variations if the description suggests different styles

OUTPUT FORMAT:
Return a JSON object with this exact structure:
{{
    "outfit_description": "A brief description of the envisioned outfit",
    "outfit_variations": [
        {{
            "variation_name": "Name of this variation",
            "variation_description": "Description of this variation",
            "outfit_items": [
                {{
                    "clothing_type": "one of the available clothing types",
                    "color": "one of the available colors or null",
                    "filters": {{
                        "material": "one of the available material building blocks or null",
                        "price_min": "minimum price or null",
                        "price_max": "maximum price or null"
                    }}
                }}
            ]
        }}
    ]
}}

VALIDATION RULES:
1. Every clothing_type must be from the available list
2. Every color must be from the available list or null
3. Every material must be from the available list or null
4. Material-color combinations must exist in the detailed inventory
5. Create at least 1 variation, maximum 3 variations
6. Each variation should have 2-5 outfit items

EXAMPLE:
For the prompt "casual summer outfit with linen shirts and blue pants", you might return:
{{
    "outfit_description": "A casual summer outfit featuring breathable linen shirts and comfortable blue pants",
    "outfit_variations": [
        {{
            "variation_name": "Casual Summer Linen",
            "variation_description": "Light and breathable summer outfit with linen shirts and blue pants",
            "outfit_items": [
                {{
                    "clothing_type": "shirts",
                    "color": "BLUE",
                    "filters": {{"material": "lin"}}
                }},
                {{
                    "clothing_type": "pants",
                    "color": "BLUE",
                    "filters": {{"material": "bomull"}}
                }}
            ]
        }}
    ]
}}

IMPORTANT: Only use items that exist in the detailed inventory. If a material-color combination doesn't exist, either omit the material filter or choose a different color that works with that material."""

        # Add retry-specific instructions
        if attempt > 0:
            system_prompt += f"\n\nRETRY ATTEMPT {attempt + 1}: Please be more careful with validation. Ensure all combinations exist in the inventory."
        
        return system_prompt

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

    def _validate_outfit_items(self, response: dict) -> None:
        """
        Validate the parsed outfit items against available inventory.
        
        Args:
            response (dict): Parsed response from OpenAI API
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(response, dict):
            raise ValueError("Response must be a dictionary")
        
        if 'outfit_description' not in response:
            raise ValueError("Response must contain 'outfit_description'")
        
        if 'outfit_variations' not in response:
            raise ValueError("Response must contain 'outfit_variations'")
        
        if not isinstance(response['outfit_variations'], list):
            raise ValueError("'outfit_variations' must be a list")
        
        if len(response['outfit_variations']) == 0:
            raise ValueError("At least one outfit variation is required")
        
        if len(response['outfit_variations']) > 3:
            raise ValueError("Maximum 3 outfit variations allowed")
        
        for variation_index, variation in enumerate(response['outfit_variations']):
            if not isinstance(variation, dict):
                raise ValueError(f"Variation {variation_index} must be a dictionary")
            
            if 'variation_name' not in variation:
                raise ValueError(f"Variation {variation_index} must contain 'variation_name'")
            
            if 'variation_description' not in variation:
                raise ValueError(f"Variation {variation_index} must contain 'variation_description'")
            
            if 'outfit_items' not in variation:
                raise ValueError(f"Variation {variation_index} must contain 'outfit_items'")
            
            if not isinstance(variation['outfit_items'], list):
                raise ValueError(f"'outfit_items' in variation {variation_index} must be a list")
            
            if len(variation['outfit_items']) == 0:
                raise ValueError(f"Variation {variation_index} must have at least one outfit item")
            
            if len(variation['outfit_items']) > 5:
                raise ValueError(f"Variation {variation_index} cannot have more than 5 outfit items")
            
            for item_index, item in enumerate(variation['outfit_items']):
                if not isinstance(item, dict):
                    raise ValueError(f"Item {item_index} in variation {variation_index} must be a dictionary")
                
                if 'clothing_type' not in item:
                    raise ValueError(f"Item {item_index} in variation {variation_index} must contain 'clothing_type'")
                
                # Validate clothing type
                if item['clothing_type'] not in self.clothing_types:
                    raise ValueError(f"Invalid clothing type '{item['clothing_type']}' in item {item_index} of variation {variation_index}. Must be one of: {', '.join(self.clothing_types)}")
                
                # Validate color if present
                if 'color' in item and item['color'] is not None:
                    if item['color'] not in self.colors:
                        raise ValueError(f"Invalid color '{item['color']}' in item {item_index} of variation {variation_index}. Must be one of: {', '.join(self.colors)}")
                
                # Validate filters if present
                if 'filters' in item and item['filters'] is not None:
                    if not isinstance(item['filters'], dict):
                        raise ValueError(f"'filters' in item {item_index} of variation {variation_index} must be a dictionary")
                    
                    # Validate material if present
                    if 'material' in item['filters'] and item['filters']['material'] is not None:
                        if item['filters']['material'] not in self.available_materials:
                            raise ValueError(f"Invalid material '{item['filters']['material']}' in item {item_index} of variation {variation_index}. Must be one of: {', '.join(self.available_materials)}")
                        
                        # Validate material-color combination exists
                        self._validate_material_color_combination_exists(item, variation_index, item_index)

    def _validate_material_color_combination_exists(self, item: dict, variation_index: int, item_index: int) -> None:
        """
        Validate that a material-color combination exists in the detailed inventory.
        
        Args:
            item (dict): Outfit item to validate
            variation_index (int): Index of the variation
            item_index (int): Index of the item
            
        Raises:
            ValueError: If the combination doesn't exist
        """
        clothing_type = item['clothing_type']
        material = item['filters'].get('material')
        color = item.get('color')
        
        if material and color:
            is_valid = validate_material_color_combination(clothing_type, material, color)
            if not is_valid:
                raise ValueError(f"Material-color combination '{material}' + '{color}' for '{clothing_type}' does not exist in inventory (item {item_index} in variation {variation_index})")

    def search_outfit_from_prompt(self, prompt: str, top_results_per_item: int = 1, 
                                 sort_by_price: bool = True, price_order: str = 'asc') -> Dict[str, List]:
        """
        Search for an outfit based on a natural language prompt.
        
        Args:
            prompt (str): Natural language outfit description
            top_results_per_item (int): Number of top results per item
            sort_by_price (bool): Whether to sort by price
            price_order (str): Sort order ('asc' or 'desc')
            
        Returns:
            Dict[str, List]: Dictionary with variation names as keys and search results as values
        """
        # Parse the prompt
        outfit_response = self.parse_outfit_prompt(prompt, max_items_per_category=top_results_per_item)
        
        # Search for each variation
        results = {}
        for variation in outfit_response['outfit_variations']:
            variation_name = variation['variation_name']
            results[variation_name] = self.search_outfit_variation(variation_name, outfit_response)
        
        return results

    def search_outfit_variation(self, variation_name: str, outfit_response: dict) -> Dict[str, List]:
        """
        Search for a specific outfit variation.
        
        Args:
            variation_name (str): Name of the variation to search for
            outfit_response (dict): Parsed outfit response
            
        Returns:
            Dict[str, List]: Search results for the variation
        """
        # Find the variation
        variation = None
        for v in outfit_response['outfit_variations']:
            if v['variation_name'] == variation_name:
                variation = v
                break
        
        if not variation:
            return {}
        
        # Search for the outfit
        outfit_items = []
        for item in variation['outfit_items']:
            outfit_items.append({
                'clothing_type': item['clothing_type'],
                'color': item.get('color'),
                'filters': item.get('filters', {})
            })
        
        return search_outfit(outfit_items, top_results_per_item=5)

def search_outfit_with_ai_prompt(api_key: str, prompt: str, top_results_per_item: int = 1,
                                sort_by_price: bool = True, price_order: str = 'asc') -> Dict[str, List]:
    """
    Convenience function to search for an outfit using AI prompt parsing.
    
    Args:
        api_key (str): OpenAI API key
        prompt (str): Natural language outfit description
        top_results_per_item (int): Number of top results per item
        sort_by_price (bool): Whether to sort by price
        price_order (str): Sort order ('asc' or 'desc')
        
    Returns:
        Dict[str, List]: Search results
    """
    parser = OutfitPromptParser(api_key)
    return parser.search_outfit_from_prompt(prompt, top_results_per_item, sort_by_price, price_order)

def test_outfit_parser():
    """Test the outfit parser functionality"""
    # Check if API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return
    
    # Test prompt
    prompt = "casual summer outfit with linen shirts"
    
    try:
        # Create parser
        parser = OutfitPromptParser(api_key)
        
        # Parse prompt
        outfit_response = parser.parse_outfit_prompt(prompt, max_items_per_category=1)
        
        # Search for outfit
        results = parser.search_outfit_from_prompt(prompt, top_results_per_item=1)
        
        return {
            'outfit_response': outfit_response,
            'search_results': results
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    test_outfit_parser() 