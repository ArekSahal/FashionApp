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
        
        print(f"🔧 Loaded database inventory:")
        print(f"   👕 Clothing Types: {len(self.clothing_types)}")
        print(f"   🎨 Colors: {len(self.colors)}")
        print(f"   🔧 Material Building Blocks: {len(self.available_materials)}")
        print(f"   📊 Detailed inventory for {len(self.detailed_inventory)} clothing types")
        
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
                print(f"\n🔄 Attempt {attempt + 1}/{max_retries} to parse outfit prompt...")
                
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
                
                # Comprehensive OpenAI API response check
                print(f"\n🔍 COMPREHENSIVE OPENAI API RESPONSE CHECK:")
                print(f"=" * 60)
                
                # Check response object structure
                print(f"📋 Response Object Type: {type(response)}")
                print(f"📋 Response Object Keys: {list(response.__dict__.keys()) if hasattr(response, '__dict__') else 'No __dict__'}")
                
                # Check if response has required attributes
                if hasattr(response, 'choices'):
                    print(f"✅ Response has 'choices' attribute")
                    print(f"📊 Number of choices: {len(response.choices)}")
                    
                    for i, choice in enumerate(response.choices):
                        print(f"   Choice {i}:")
                        print(f"     Type: {type(choice)}")
                        print(f"     Keys: {list(choice.__dict__.keys()) if hasattr(choice, '__dict__') else 'No __dict__'}")
                        
                        if hasattr(choice, 'message'):
                            print(f"     ✅ Choice has 'message' attribute")
                            message = choice.message
                            print(f"     Message type: {type(message)}")
                            print(f"     Message keys: {list(message.__dict__.keys()) if hasattr(message, '__dict__') else 'No __dict__'}")
                            
                            if hasattr(message, 'content'):
                                print(f"     ✅ Message has 'content' attribute")
                                print(f"     Content type: {type(message.content)}")
                                print(f"     Content length: {len(message.content) if message.content else 0}")
                                print(f"     Content preview: {message.content[:200] if message.content else 'None'}...")
                            else:
                                print(f"     ❌ Message missing 'content' attribute")
                        else:
                            print(f"     ❌ Choice missing 'message' attribute")
                else:
                    print(f"❌ Response missing 'choices' attribute")
                
                # Check usage information
                if hasattr(response, 'usage'):
                    print(f"📊 Usage Information:")
                    usage = response.usage
                    print(f"   Usage type: {type(usage)}")
                    print(f"   Usage keys: {list(usage.__dict__.keys()) if hasattr(usage, '__dict__') else 'No __dict__'}")
                    if hasattr(usage, 'prompt_tokens'):
                        print(f"   Prompt tokens: {usage.prompt_tokens}")
                    if hasattr(usage, 'completion_tokens'):
                        print(f"   Completion tokens: {usage.completion_tokens}")
                    if hasattr(usage, 'total_tokens'):
                        print(f"   Total tokens: {usage.total_tokens}")
                else:
                    print(f"⚠️  No usage information available")
                
                # Check model information
                if hasattr(response, 'model'):
                    print(f"🤖 Model used: {response.model}")
                else:
                    print(f"⚠️  No model information available")
                
                # Check for any error information
                if hasattr(response, 'error'):
                    print(f"❌ Error in response: {response.error}")
                
                # Final content check
                print(f"\n📝 FINAL CONTENT ANALYSIS:")
                print(f"Raw content: {repr(content)}")
                print(f"Content length: {len(content)}")
                print(f"Content starts with: {content[:50] if content else 'None'}")
                print(f"Content ends with: {content[-50:] if content else 'None'}")
                
                # Check if content looks like JSON
                content_stripped = content.strip()
                if content_stripped.startswith('{') and content_stripped.endswith('}'):
                    print(f"✅ Content appears to be JSON (starts with {{ and ends with }})")
                elif content_stripped.startswith('[') and content_stripped.endswith(']'):
                    print(f"✅ Content appears to be JSON array (starts with [ and ends with ])")
                else:
                    print(f"⚠️  Content doesn't appear to be JSON format")
                    print(f"   First 100 chars: {content[:100]}")
                    print(f"   Last 100 chars: {content[-100:]}")
                
                print(f"=" * 60)
                
                # Parse the JSON response
                parsed_response = json.loads(content)
                
                # Validate the response
                self._validate_outfit_items(parsed_response)
                
                print(f"✅ Successfully parsed and validated outfit prompt on attempt {attempt + 1}")
                return parsed_response
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to parse OpenAI response as JSON after {max_retries} attempts: {e}")
                continue
                
            except ValueError as e:
                print(f"❌ Validation error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise e
                # Continue to next attempt with enhanced prompt
                continue
                
            except Exception as e:
                print(f"❌ Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"OpenAI API error after {max_retries} attempts: {e}")
                continue
        
        raise Exception(f"Failed to parse outfit prompt after {max_retries} attempts")
    
    def _create_system_prompt(self, detailed_inventory_text: str, max_items_per_category: int, attempt: int = 0) -> str:
        """
        Create the system prompt with validation instructions.
        
        Args:
            detailed_inventory_text (str): Formatted detailed inventory information
            max_items_per_category (int): Maximum items per category
            attempt (int): Current attempt number (for retry logic)
            
        Returns:
            str: System prompt
        """
        # Add retry-specific instructions if this is not the first attempt
        retry_instructions = ""
        if attempt > 0:
            retry_instructions = f"""

IMPORTANT - THIS IS ATTEMPT {attempt + 1}:
The previous attempt failed validation because it used material-color combinations that don't exist in the database.
Please be EXTRA CAREFUL to only use combinations that are explicitly listed in the detailed inventory above.
Double-check every material-color combination before including it in your response.
"""
        
        return f"""
You are a fashion stylist. Convert natural language outfit descriptions into THREE UNIQUE outfit variations with structured search parameters.

Available clothing types (use these exact names): {', '.join(self.clothing_types)}
Available colors (use these exact names): {', '.join(self.colors)}
Available material building blocks (use these exact names): {', '.join(self.available_materials)}

DETAILED INVENTORY BY CLOTHING TYPE:
{detailed_inventory_text}

CRITICAL VALIDATION RULES - READ CAREFULLY:
1. Do not include shoes
2. Use only exact clothing type names from the clothing types list above
3. Use only exact color names from the colors list above
4. Use only exact material building block names from the materials list above
5. ALWAYS check the detailed inventory above to ensure material-color combinations actually exist
6. Use "q" parameter only for specific clothing types (e.g., "chino", "box-shirt", "short sleeve")
7. Do not use "style" parameter in filters
8. Create THREE DISTINCT outfit variations that interpret the prompt differently
9. Each outfit should have a unique style approach, color palette, or clothing combination
10. For materials, use the building block names (e.g., "lin", "bomull", "ull") - these will match partial material strings like "55% lin, 45% bomull"
11. ONLY use material-color combinations that are listed in the detailed inventory above
12. If a material-color combination is not listed in the detailed inventory, DO NOT use it - choose a different combination that exists
13. The system will automatically reject any outfit that uses non-existent combinations, so be very careful

VALIDATION PROCESS:
- Before suggesting any material-color combination, check the detailed inventory
- Look for the clothing type in the inventory
- Check if the material is listed for that clothing type
- Check if the color is listed for that clothing type  
- Check if the specific material-color combination exists
- If any of these checks fail, choose a different combination that exists

{retry_instructions}

For each outfit description:
1. Identify key clothing items needed (excluding shoes)
2. Check the detailed inventory to see what materials and colors are available for each clothing type
3. Choose materials and colors that have valid combinations in the inventory
4. Use "q" parameter only for specific clothing types
5. Generate a clear outfit description for each variation

Return JSON with this structure:
{{
    "outfit_description": "Overall description of the style direction and how the three variations interpret the prompt",
    "outfit_variations": [
        {{
            "variation_name": "Name for this outfit variation (e.g., 'Classic Elegant', 'Modern Casual', 'Bold Statement')",
            "variation_description": "Description of this specific outfit variation",
            "outfit_items": [
                {{
                    "clothing_type": "shirts",
                    "color": "BROWN",
                    "filters": {{"material": "lin", "q": "short sleeve"}},
                    "max_items": {max_items_per_category}
                }}
            ]
        }}
    ]
}}

Example input: "old money summer vibe with deep autumn colors"
Example output: {{
    "outfit_description": "Three sophisticated summer outfit interpretations of the old money aesthetic, each featuring deep autumn colors but with distinct approaches: classic elegance, modern refinement, and bold sophistication.",
    "outfit_variations": [
        {{
            "variation_name": "Classic Elegant",
            "variation_description": "A timeless summer outfit featuring a refined linen shirt in warm brown tones paired with beige chino pants, creating a sophisticated and polished look perfect for summer events.",
            "outfit_items": [
                {{
                    "clothing_type": "shirts",
                    "color": "BROWN",
                    "filters": {{"material": "lin", "q": "short sleeve"}},
                    "max_items": {max_items_per_category}
                }},
                {{
                    "clothing_type": "pants",
                    "color": "BEIGE",
                    "filters": {{"material": "lin", "q": "chino"}},
                    "max_items": {max_items_per_category}
                }}
            ]
        }},
        {{
            "variation_name": "Modern Refined",
            "variation_description": "A contemporary take on old money style with a structured blazer in deep olive paired with a crisp white shirt and tailored trousers, offering a sophisticated business-casual approach.",
            "outfit_items": [
                {{
                    "clothing_type": "shirts",
                    "color": "WHITE",
                    "filters": {{"material": "bomull", "q": "oxford"}},
                    "max_items": {max_items_per_category}
                }},
                {{
                    "clothing_type": "jackets",
                    "color": "OLIVE",
                    "filters": {{"material": "bomull"}},
                    "max_items": {max_items_per_category}
                }},
                {{
                    "clothing_type": "pants",
                    "color": "BROWN",
                    "filters": {{"material": "bomull"}},
                    "max_items": {max_items_per_category}
                }}
            ]
        }},
        {{
            "variation_name": "Bold Sophistication",
            "variation_description": "A statement-making outfit with a deep burgundy sweater paired with charcoal trousers, creating a rich, luxurious look that embodies old money confidence.",
            "outfit_items": [
                {{
                    "clothing_type": "sweaters",
                    "color": "RED",
                    "filters": {{"material": "ull"}},
                    "max_items": {max_items_per_category}
                }},
                {{
                    "clothing_type": "pants",
                    "color": "GRAY",
                    "filters": {{"material": "bomull"}},
                    "max_items": {max_items_per_category}
                }}
            ]
        }}
    ]
}}

Return ONLY the JSON object, no additional text.
"""

    def _format_detailed_inventory_for_ai(self) -> str:
        """
        Format the detailed inventory information for the AI model in a readable format.
        
        Returns:
            str: Formatted inventory information
        """
        if not self.detailed_inventory:
            return "No detailed inventory available."
        
        formatted_text = ""
        
        for clothing_type, data in self.detailed_inventory.items():
            formatted_text += f"\n{clothing_type.upper()} ({data['product_count']} products):\n"
            formatted_text += f"  Available materials: {', '.join(data['materials'])}\n"
            formatted_text += f"  Available colors: {', '.join(data['colors'])}\n"
            
            if data['material_color_combinations']:
                formatted_text += f"  Material-Color combinations:\n"
                for material, colors in data['material_color_combinations'].items():
                    if colors:  # Only show materials that have colors
                        formatted_text += f"    {material}: {', '.join(colors)}\n"
            
            formatted_text += "\n"
        
        return formatted_text

    def _validate_outfit_items(self, response: dict) -> None:
        """
        Validate the outfit response returned by OpenAI.
        
        Args:
            response (dict): Response dictionary containing outfit_description and outfit_items
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(response, dict):
            raise ValueError("Response must be a dictionary with outfit_description and outfit_items")
        
        # Validate outfit_description
        if 'outfit_description' not in response:
            raise ValueError("Response missing 'outfit_description' field")
        
        if not isinstance(response['outfit_description'], str):
            raise ValueError("'outfit_description' must be a string")
        
        if not response['outfit_description'].strip():
            raise ValueError("'outfit_description' cannot be empty")
        
        # Validate outfit_items
        if 'outfit_variations' not in response:
            raise ValueError("Response missing 'outfit_variations' field")
        
        outfit_variations = response['outfit_variations']
        
        if not isinstance(outfit_variations, list):
            raise ValueError("'outfit_variations' must be a list")
        
        for i, variation in enumerate(outfit_variations):
            if not isinstance(variation, dict):
                raise ValueError(f"Variation {i} must be a dictionary")
            
            # Check required fields
            if 'variation_name' not in variation:
                raise ValueError(f"Variation {i} missing 'variation_name' field")
            
            if 'variation_description' not in variation:
                raise ValueError(f"Variation {i} missing 'variation_description' field")
            
            if 'outfit_items' not in variation:
                raise ValueError(f"Variation {i} missing 'outfit_items' field")
            
            outfit_items = variation['outfit_items']
            
            if not isinstance(outfit_items, list):
                raise ValueError(f"Variation {i} 'outfit_items' must be a list")
            
            for j, item in enumerate(outfit_items):
                if not isinstance(item, dict):
                    raise ValueError(f"Item {j} in variation {i} must be a dictionary")
                
                # Check required fields
                if 'clothing_type' not in item:
                    raise ValueError(f"Item {j} in variation {i} missing 'clothing_type' field")
                
                # Validate clothing type
                if item['clothing_type'] not in self.clothing_types:
                    raise ValueError(f"Item {j} in variation {i} has invalid clothing_type: {item['clothing_type']}. Must be one of: {', '.join(self.clothing_types)}")
                
                # Validate color if present
                if 'color' in item and item['color']:
                    if item['color'] not in self.colors:
                        raise ValueError(f"Item {j} in variation {i} has invalid color: {item['color']}. Must be one of: {', '.join(self.colors)}")
                
                # Validate materials in filters if present
                if 'filters' in item and isinstance(item['filters'], dict):
                    for material_key in ['material', 'upper_material']:
                        if material_key in item['filters'] and item['filters'][material_key]:
                            material_value = item['filters'][material_key]
                            if material_value not in self.available_materials:
                                raise ValueError(f"Item {j} in variation {i} has invalid material '{material_value}' in {material_key}. Must be one of: {', '.join(self.available_materials)}")
                    
                    # Reject style parameter - should use q instead
                    if 'style' in item['filters']:
                        raise ValueError(f"Item {j} in variation {i} uses 'style' parameter in filters. Use 'q' parameter for specific clothing types instead.")
                    
                    # Validate q parameter usage
                    if 'q' in item['filters']:
                        q_value = item['filters']['q']
                        # List of style descriptors that should NOT be used in q parameter
                        style_descriptors = [
                            'casual', 'minimalistic', 'elegant', 'formal', 'sophisticated', 
                            'trendy', 'classic', 'modern', 'vintage', 'streetwear', 'business',
                            'old money', 'scandinavian', 'minimalist', 'chic', 'stylish',
                            'fashionable', 'trendy', 'contemporary', 'traditional'
                        ]
                        
                        if q_value.lower() in [desc.lower() for desc in style_descriptors]:
                            raise ValueError(f"Item {j} in variation {i} uses style descriptor '{q_value}' in q parameter. The q parameter should only be used for specific clothing types (e.g., 'chino', 'box-shirt', 'short sleeve'), not style descriptors.")
                
                # Validate filters if present
                if 'filters' in item and not isinstance(item['filters'], dict):
                    raise ValueError(f"Item {j} in variation {i} 'filters' must be a dictionary")
                
                # CRITICAL: Validate material-color combinations exist in database
                self._validate_material_color_combination_exists(item, i, j)
    
    def _validate_material_color_combination_exists(self, item: dict, variation_index: int, item_index: int) -> None:
        """
        Validate that the material-color combination actually exists in the database.
        
        Args:
            item (dict): The outfit item to validate
            variation_index (int): Index of the variation for error reporting
            item_index (int): Index of the item for error reporting
            
        Raises:
            ValueError: If the combination doesn't exist
        """
        clothing_type = item.get('clothing_type')
        color = item.get('color')
        filters = item.get('filters', {})
        
        # Get material from filters
        material = filters.get('material') or filters.get('upper_material')
        
        # If we have both material and color, validate the combination
        if material and color and clothing_type:
            # Check if this clothing type exists in detailed inventory
            if clothing_type not in self.detailed_inventory:
                raise ValueError(f"Item {item_index} in variation {variation_index} references clothing type '{clothing_type}' which is not in the detailed inventory. Available types: {', '.join(self.detailed_inventory.keys())}")
            
            clothing_data = self.detailed_inventory[clothing_type]
            
            # Check if material exists for this clothing type
            if material not in clothing_data['materials']:
                available_materials = ', '.join(clothing_data['materials'])
                raise ValueError(f"Item {item_index} in variation {variation_index} uses material '{material}' for {clothing_type}, but this material is not available. Available materials for {clothing_type}: {available_materials}")
            
            # Check if color exists for this clothing type
            if color not in clothing_data['colors']:
                available_colors = ', '.join(clothing_data['colors'])
                raise ValueError(f"Item {item_index} in variation {variation_index} uses color '{color}' for {clothing_type}, but this color is not available. Available colors for {clothing_type}: {available_colors}")
            
            # Check if the specific material-color combination exists
            material_combinations = clothing_data['material_color_combinations']
            if material not in material_combinations:
                raise ValueError(f"Item {item_index} in variation {variation_index} uses material '{material}' for {clothing_type}, but no material-color combinations are available for this material.")
            
            if color not in material_combinations[material]:
                available_colors_for_material = ', '.join(material_combinations[material])
                raise ValueError(f"Item {item_index} in variation {variation_index} uses material '{material}' with color '{color}' for {clothing_type}, but this combination doesn't exist. Available colors for {material} in {clothing_type}: {available_colors_for_material}")
            
            print(f"✅ Validated combination: {clothing_type} + {material} + {color} exists in database")

    def search_outfit_from_prompt(self, prompt: str, top_results_per_item: int = 1, 
                                 sort_by_price: bool = True, price_order: str = 'asc') -> Dict[str, List]:
        """
        Parse a prompt and search for multiple outfit variations in one step.
        
        Args:
            prompt (str): Natural language outfit description
            top_results_per_item (int): Number of top results to return per item (should be 1 for distinct outfits)
            sort_by_price (bool): Whether to sort results by price
            price_order (str): Sort order for price ('asc' or 'desc')
            
        Returns:
            Dict[str, List]: Dictionary with outfit variation names as keys and lists of products as values
        """
        print(f"Parsing prompt: '{prompt}'")
        
        # Parse the prompt into outfit variations
        outfit_response = self.parse_outfit_prompt(prompt)
        
        # Display the outfit description
        print(f"\n🎨 Outfit Vision:")
        print(f"   {outfit_response['outfit_description']}")
        
        print(f"\nGenerated {len(outfit_response['outfit_variations'])} outfit variations:")
        for i, variation in enumerate(outfit_response['outfit_variations'], 1):
            print(f"  {i}. {variation['variation_name']} - {variation['variation_description']}")
            for j, item in enumerate(variation['outfit_items'], 1):
                print(f"    {j}. {item['clothing_type']} - Color: {item.get('color', 'Any')} - Filters: {item.get('filters', {})}")
        
        # Search for each outfit variation
        all_results = {}
        
        for variation in outfit_response['outfit_variations']:
            variation_name = variation['variation_name']
            print(f"\n🔍 Searching for variation: {variation_name}")
            
            # Search for this variation's items
            variation_results = search_outfit(
                outfit_items=variation['outfit_items'],
                top_results_per_item=top_results_per_item,
                sort_by_price=sort_by_price,
                price_order=price_order
            )
            
            # Store results with variation name as key
            all_results[variation_name] = {
                'variation_description': variation['variation_description'],
                'products': variation_results
            }
        
        return all_results

def search_outfit_with_ai_prompt(api_key: str, prompt: str, top_results_per_item: int = 1,
                                sort_by_price: bool = True, price_order: str = 'asc') -> Dict[str, List]:
    """
    Convenience function to search for an outfit using a natural language prompt.
    
    Args:
        api_key (str): OpenAI API key
        prompt (str): Natural language outfit description
        top_results_per_item (int): Number of top results to return per item
        sort_by_price (bool): Whether to sort results by price
        price_order (str): Sort order for price ('asc' or 'desc')
        
    Returns:
        dict: Dictionary with clothing types as keys and lists of products as values
    """
    parser = OutfitPromptParser(api_key)
    return parser.search_outfit_from_prompt(
        prompt=prompt,
        top_results_per_item=top_results_per_item,
        sort_by_price=sort_by_price,
        price_order=price_order
    )

# Example usage
if __name__ == "__main__":
    # You'll need to set your OpenAI API key
    import os
    
    # Get API key from environment variable (recommended for security)
    api_key = Config.OPENAI_API_KEY
    
    if not api_key:
        print("Please set your OPENAI_API_KEY environment variable")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        exit(1)
    
    # Example prompts to test
    test_prompts = [
        "old money summer vibe with deep autumn colors",
        "minimalist Scandinavian style with neutral tones",
        #"streetwear aesthetic with bold colors",
        #"business casual for a tech startup",
        #"vintage 90s grunge look"
    ]
    
    parser = OutfitPromptParser(api_key)
    
    for prompt in test_prompts:
        print(f"\n{'='*60}")
        print(f"Testing prompt: '{prompt}'")
        print('='*60)
        
        try:
            # Parse the prompt
            outfit_response = parser.parse_outfit_prompt(prompt)
            
            print(f"\n🎨 Outfit Vision:")
            print(f"   {outfit_response['outfit_description']}")
            
            print(f"\nParsed outfit variations:")
            for i, variation in enumerate(outfit_response['outfit_variations'], 1):
                print(f"  {i}. {variation['variation_name']} - {variation['variation_description']}")
                for j, item in enumerate(variation['outfit_items'], 1):
                    print(f"    {j}. {item['clothing_type']}")
                    if 'color' in item:
                        print(f"     Color: {item['color']}")
                    if 'filters' in item:
                        print(f"     Filters: {item['filters']}")
            
            # Search for the outfit (uncomment to actually search)
            # results = parser.search_outfit_from_prompt(prompt, top_results_per_item=2)
            # print(f"\nFound {sum(len(products) for products in results.values())} total products")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "-"*60) 