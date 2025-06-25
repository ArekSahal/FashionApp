#!/usr/bin/env python3
"""
Example demonstration of the detailed inventory system.

This script shows how the detailed inventory system works
without requiring a real database connection.
"""

def create_sample_detailed_inventory():
    """Create sample detailed inventory data for demonstration"""
    return {
        'shirts': {
            'product_count': 45,
            'materials': ['lin', 'bomull', 'polyester', 'siden'],
            'colors': ['BLUE', 'WHITE', 'BLACK', 'RED', 'GREEN'],
            'material_color_combinations': {
                'lin': ['BLUE', 'WHITE', 'BEIGE', 'BROWN'],
                'bomull': ['BLUE', 'WHITE', 'BLACK', 'RED', 'GREEN'],
                'polyester': ['BLUE', 'BLACK', 'RED'],
                'siden': ['BLUE', 'WHITE', 'BLACK']
            }
        },
        'pants': {
            'product_count': 32,
            'materials': ['bomull', 'lin', 'polyester', 'denim'],
            'colors': ['BLUE', 'BLACK', 'WHITE', 'BEIGE', 'GRAY'],
            'material_color_combinations': {
                'bomull': ['BLUE', 'BLACK', 'WHITE', 'BEIGE'],
                'lin': ['BLUE', 'BEIGE', 'BROWN'],
                'polyester': ['BLACK', 'BLUE', 'GRAY'],
                'denim': ['BLUE', 'BLACK']
            }
        },
        'sweaters': {
            'product_count': 28,
            'materials': ['ull', 'kaschmir', 'akryl', 'bomull'],
            'colors': ['BLUE', 'BLACK', 'WHITE', 'GRAY', 'BROWN'],
            'material_color_combinations': {
                'ull': ['BLUE', 'BLACK', 'GRAY', 'BROWN'],
                'kaschmir': ['BLUE', 'BLACK', 'GRAY'],
                'akryl': ['BLUE', 'BLACK', 'WHITE'],
                'bomull': ['BLUE', 'WHITE', 'BLACK']
            }
        }
    }

def format_detailed_inventory_for_ai(detailed_inventory):
    """Format detailed inventory for AI consumption"""
    formatted_lines = []
    
    for clothing_type, data in detailed_inventory.items():
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

def create_ai_system_prompt(detailed_inventory_text):
    """Create AI system prompt with detailed inventory"""
    return f"""You are an expert fashion stylist. Use ONLY the available inventory below:

AVAILABLE INVENTORY:
{detailed_inventory_text}

RULES:
1. Only suggest clothing types that exist in the inventory
2. Only suggest colors that exist for each clothing type
3. Only suggest material-color combinations that are valid
4. If a combination doesn't exist, either omit the material or choose a different color

EXAMPLE VALID SUGGESTIONS:
- "Blue linen shirts" ✅ (lin + BLUE exists for shirts)
- "White cotton pants" ✅ (bomull + WHITE exists for pants)
- "Black wool sweaters" ✅ (ull + BLACK exists for sweaters)

EXAMPLE INVALID SUGGESTIONS:
- "Red linen shirts" ❌ (lin + RED doesn't exist for shirts)
- "Silk pants" ❌ (siden doesn't exist for pants)
- "Green cashmere sweaters" ❌ (kaschmir + GREEN doesn't exist for sweaters)"""

def validate_material_color_combination(detailed_inventory, clothing_type, material, color):
    """Validate if a material-color combination exists"""
    if clothing_type not in detailed_inventory:
        return False, f"Clothing type '{clothing_type}' not found"
    
    data = detailed_inventory[clothing_type]
    
    if material not in data['materials']:
        return False, f"Material '{material}' not available for {clothing_type}"
    
    if color not in data['colors']:
        return False, f"Color '{color}' not available for {clothing_type}"
    
    if material in data['material_color_combinations']:
        if color in data['material_color_combinations'][material]:
            return True, "Valid combination"
        else:
            return False, f"Material '{material}' not available in color '{color}' for {clothing_type}"
    
    return False, f"Material '{material}' has no color combinations defined for {clothing_type}"

def demonstrate_system():
    """Demonstrate the detailed inventory system"""
    try:
        # Create sample data
        detailed_inventory = create_sample_detailed_inventory()
        
        # Format for AI
        formatted_inventory = format_detailed_inventory_for_ai(detailed_inventory)
        
        # Create AI system prompt
        system_prompt = create_ai_system_prompt(formatted_inventory)
        
        # Test some combinations
        test_combinations = [
            ('shirts', 'lin', 'BLUE'),
            ('shirts', 'lin', 'RED'),
            ('pants', 'bomull', 'WHITE'),
            ('pants', 'siden', 'BLUE'),
            ('sweaters', 'ull', 'BLACK'),
            ('sweaters', 'kaschmir', 'GREEN')
        ]
        
        results = []
        for clothing_type, material, color in test_combinations:
            is_valid, reason = validate_material_color_combination(detailed_inventory, clothing_type, material, color)
            results.append({
                'clothing_type': clothing_type,
                'material': material,
                'color': color,
                'valid': is_valid,
                'reason': reason
            })
        
        return {
            'detailed_inventory': detailed_inventory,
            'formatted_inventory': formatted_inventory,
            'system_prompt': system_prompt,
            'test_results': results
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    demonstrate_system() 