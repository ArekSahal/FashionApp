# Dynamic Material Building Blocks and AI Data System

## Overview

This system provides dynamic material building blocks extraction and comprehensive data structures for AI decision-making in fashion applications. It analyzes the database inventory to provide granular information about clothing types, materials, colors, and their combinations.

## Key Features

### 1. Dynamic Material Building Blocks

The system dynamically extracts material building blocks from the database instead of relying on a static list. This ensures that the AI has access to all materials that actually exist in the inventory.

#### Functions:
- `build_dynamic_material_building_blocks()`: Extracts all unique material building blocks from the database
- `extract_material_building_blocks_dynamic()`: Enhanced material extraction using regex patterns and percentage detection

#### Example:
```python
# Get all material building blocks that exist in the database
dynamic_materials = build_dynamic_material_building_blocks()
print(f"Found {len(dynamic_materials)} materials: {sorted(list(dynamic_materials))}")
```

### 2. Comprehensive AI Data

The system provides comprehensive data structures that give the AI all the granularity it needs to make informed decisions.

#### Functions:
- `get_comprehensive_ai_data()`: Returns complete database analysis
- `get_ai_decision_support_data()`: Optimized data structure for AI decision-making
- `get_material_color_availability_matrix()`: Matrix showing material-color availability

#### Data Structure:
```python
{
    'statistics': {
        'total_products': 1000,
        'total_clothing_types': 15,
        'total_materials': 25,
        'total_colors': 30,
        'total_combinations': 500
    },
    'clothing_types': ['sweaters', 'pants', 'shirts', ...],
    'materials': {
        'raw_materials': ['55% lin, 45% bomull', '100% polyester', ...],
        'building_blocks': ['lin', 'bomull', 'polyester', ...]
    },
    'colors': ['BLUE', 'BLACK', 'WHITE', 'RED', ...],
    'combinations': {
        'sweaters': {
            'lin': {'BLUE': 15, 'BLACK': 8, 'WHITE': 12},
            'bomull': {'BLUE': 20, 'RED': 5, ...}
        },
        ...
    }
}
```

### 3. Combination Validation and Suggestions

The system can validate if specific combinations exist and suggest optimal outfit combinations.

#### Functions:
- `validate_combination_exists(clothing_type, material, color)`: Check if a combination exists
- `get_best_available_combinations()`: Get best combinations with preferences
- `suggest_outfit_combinations()`: Suggest complete outfit combinations

#### Examples:
```python
# Check if a combination exists
exists, count = validate_combination_exists('sweaters', 'lin', 'BLUE')
print(f"Blue linen sweaters: {exists} ({count} products)")

# Get best combinations with preferences
best_combinations = get_best_available_combinations(
    'sweaters',
    preferred_materials=['lin', 'bomull'],
    preferred_colors=['BLUE', 'BLACK'],
    min_products=1
)

# Suggest outfit combinations
suggestions = suggest_outfit_combinations(
    preferred_materials=['lin', 'bomull'],
    preferred_colors=['BLUE', 'BLACK', 'WHITE'],
    max_suggestions=5
)
```

## Usage Examples

### 1. Getting AI Decision Support Data

```python
from search_function import get_ai_decision_support_data

# Get comprehensive data for AI decision-making
ai_data = get_ai_decision_support_data()

# Access different data types
print(f"Total combinations: {len(ai_data['all_valid_combinations'])}")
print(f"Available clothing types: {ai_data['clothing_types']}")
print(f"Available materials: {ai_data['materials']['building_blocks']}")
print(f"Available colors: {ai_data['colors']}")

# Get frequency data
material_freq = ai_data['material_frequency_by_clothing_type']
color_freq = ai_data['color_frequency_by_clothing_type']

# Get examples
examples = ai_data['examples']
print(f"Most common materials: {examples['most_common_materials']}")
print(f"Most common colors: {examples['most_common_colors']}")
```

### 2. Material-Color Availability Matrix

```python
from search_function import get_material_color_availability_matrix

# Get availability matrix
matrix = get_material_color_availability_matrix()

# Check what colors are available for a specific material and clothing type
sweater_colors = matrix.get('sweaters', {}).get('lin', [])
print(f"Blue linen sweaters available: {'BLUE' in sweater_colors}")

# Get all materials available for a clothing type
sweater_materials = list(matrix.get('sweaters', {}).keys())
print(f"Materials available for sweaters: {sweater_materials}")
```

### 3. Combination Validation

```python
from search_function import validate_combination_exists

# Test various combinations
combinations_to_test = [
    ('sweaters', 'lin', 'BLUE'),
    ('pants', 'bomull', 'BLACK'),
    ('shirts', 'polyester', 'WHITE'),
    ('t_shirts', 'bomull', 'RED')
]

for clothing_type, material, color in combinations_to_test:
    exists, count = validate_combination_exists(clothing_type, material, color)
    status = "✓ EXISTS" if exists else "✗ NOT FOUND"
    print(f"{clothing_type} + {material} + {color}: {status} ({count} products)")
```

### 4. Outfit Suggestions

```python
from search_function import suggest_outfit_combinations

# Get outfit suggestions based on preferences
suggestions = suggest_outfit_combinations(
    target_style='casual',
    preferred_materials=['lin', 'bomull'],
    preferred_colors=['BLUE', 'BLACK', 'WHITE'],
    max_suggestions=5
)

# Display suggestions
for i, suggestion in enumerate(suggestions, 1):
    print(f"\n{i}. {suggestion['outfit_type']} (Score: {suggestion['compatibility_score']:.2f})")
    print(f"   Top: {suggestion['top']['material']} + {suggestion['top']['color']}")
    print(f"   Bottom: {suggestion['bottom']['material']} + {suggestion['bottom']['color']}")
    print(f"   Total Products: {suggestion['total_products']}")
```

## Testing

Run the test script to see all functionality in action:

```bash
cd ai_server
python test_dynamic_materials.py
```

This will test:
- Dynamic material building blocks extraction
- Comprehensive AI data generation
- Material-color availability matrix
- Combination validation
- Best combinations with preferences
- AI decision support data
- Outfit combination suggestions

## Benefits for AI Decision-Making

### 1. Granular Data Access
The AI now has access to:
- All clothing types in the inventory
- All material building blocks that actually exist
- All colors available
- Exact product counts for each combination
- Material and color frequency data

### 2. Validation Capabilities
The AI can:
- Validate if requested combinations exist
- Get product counts for combinations
- Understand availability constraints
- Make informed decisions based on actual inventory

### 3. Optimization Features
The AI can:
- Prioritize combinations with higher product counts
- Consider material and color preferences
- Suggest compatible outfit combinations
- Avoid suggesting unavailable combinations

### 4. Real-time Updates
Since the system builds material building blocks dynamically from the database:
- New materials are automatically detected
- Material availability is always current
- No manual updates required for new materials

## Integration with AI Systems

The data structures are designed to be easily consumed by AI systems:

```python
# Example: Providing context to an AI system
ai_data = get_ai_decision_support_data()

# Send to AI system
ai_context = {
    "available_combinations": ai_data['all_valid_combinations'],
    "material_frequency": ai_data['material_frequency_by_clothing_type'],
    "color_frequency": ai_data['color_frequency_by_clothing_type'],
    "availability_matrix": ai_data['availability_matrix'],
    "statistics": ai_data['statistics']
}

# AI can now make informed decisions about:
# - What combinations to suggest
# - What alternatives to offer when preferred combinations aren't available
# - How to prioritize suggestions based on availability
# - What outfit combinations work well together
```

## Performance Considerations

- The system caches data during execution for efficiency
- Database queries are optimized to minimize load times
- Large datasets are processed incrementally
- Results are sorted and limited to prevent memory issues

## Future Enhancements

Potential improvements could include:
- Caching mechanisms for frequently accessed data
- Real-time updates when inventory changes
- Machine learning integration for better suggestions
- Seasonal trend analysis
- Price-based optimization
- Style compatibility scoring 