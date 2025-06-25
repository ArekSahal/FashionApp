# API Changes Documentation

## Overview
The outfit search API has been updated to generate **three unique outfit variations** instead of one, and now returns the **best single item** from each clothing category to create distinct, cohesive outfits.

## Key Changes

### 1. Response Structure Changes

#### Old Response Structure (Before)
```json
{
  "success": true,
  "outfit_description": "Description of the outfit style",
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
```

#### New Response Structure (After)
```json
{
  "success": true,
  "outfit_description": "Overall description of the style direction and how the three variations interpret the prompt",
  "outfits": [
    {
      "outfit_id": 1,
      "variation_name": "Classic Elegant",
      "variation_description": "A timeless summer look featuring a lightweight brown linen short-sleeve shirt paired with beige linen chino pants for a refined and effortless old money appeal.",
      "items": [
        {
          "clothing_type": "shirts",
          "name": "Product Name",
          "price": "499,00 kr",
          "url": "https://...",
          "image_url": "https://...",
          "secondary_image_url": "https://..."
        }
      ]
    },
    {
      "outfit_id": 2,
      "variation_name": "Modern Refined",
      "variation_description": "A sleek take on old money summer style with a beige linen suit layered over an olive short-sleeve cotton shirt, offering a polished and contemporary aesthetic.",
      "items": [
        {
          "clothing_type": "suits",
          "name": "Product Name",
          "price": "1,299,00 kr",
          "url": "https://...",
          "image_url": "https://...",
          "secondary_image_url": "https://..."
        },
        {
          "clothing_type": "shirts",
          "name": "Product Name",
          "price": "399,00 kr",
          "url": "https://...",
          "image_url": "https://...",
          "secondary_image_url": "https://..."
        }
      ]
    },
    {
      "outfit_id": 3,
      "variation_name": "Bold Statement",
      "variation_description": "A casual yet striking ensemble with a gold cotton box-style tee and olive denim jeans, blending deep autumn hues with a relaxed old money vibe.",
      "items": [
        {
          "clothing_type": "t_shirts",
          "name": "Product Name",
          "price": "299,00 kr",
          "url": "https://...",
          "image_url": "https://...",
          "secondary_image_url": "https://..."
        },
        {
          "clothing_type": "jeans",
          "name": "Product Name",
          "price": "799,00 kr",
          "url": "https://...",
          "image_url": "https://...",
          "secondary_image_url": "https://..."
        }
      ]
    }
  ],
  "total_outfits": 3,
  "total_products": 6,
  "search_metadata": {
    "prompt": "old money summer vibe with deep autumn colors",
    "top_results_per_item": 1,
    "sort_by_price": true,
    "price_order": "asc",
    "variations_searched": ["Classic Elegant", "Modern Refined", "Bold Statement"]
  }
}
```

### 2. New Fields in Outfit Objects

Each outfit object now includes:
- **`variation_name`**: Descriptive name for the outfit style (e.g., "Classic Elegant", "Modern Refined", "Bold Statement")
- **`variation_description`**: Detailed description explaining the specific style approach and how pieces work together

### 3. Default Parameter Changes

- **`top_results_per_item`**: Changed from `3` to `1` (now takes the best single item from each category)
- This ensures each outfit variation is distinct and cohesive

### 4. Search Metadata Updates

- **`clothing_types_searched`** → **`variations_searched`**: Now lists the variation names instead of clothing types

## Frontend Implementation Guide

### 1. Display Multiple Outfits

Instead of showing one outfit, your UI should now display three distinct outfit variations:

```javascript
// Example React/Vue component structure
const OutfitDisplay = ({ outfitData }) => {
  return (
    <div className="outfits-container">
      <h2>Outfit Variations</h2>
      <p className="overall-description">{outfitData.outfit_description}</p>
      
      {outfitData.outfits.map((outfit) => (
        <div key={outfit.outfit_id} className="outfit-variation">
          <h3>{outfit.variation_name}</h3>
          <p className="variation-description">{outfit.variation_description}</p>
          
          <div className="outfit-items">
            {outfit.items.map((item, index) => (
              <div key={index} className="outfit-item">
                <img src={item.image_url} alt={item.name} />
                <h4>{item.name}</h4>
                <p>{item.price}</p>
                <a href={item.url} target="_blank">View Product</a>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};
```

### 2. UI Layout Suggestions

#### Option A: Horizontal Layout
```
[Outfit 1: Classic Elegant] [Outfit 2: Modern Refined] [Outfit 3: Bold Statement]
```

#### Option B: Vertical Layout
```
Outfit 1: Classic Elegant
[Items displayed horizontally]

Outfit 2: Modern Refined  
[Items displayed horizontally]

Outfit 3: Bold Statement
[Items displayed horizontally]
```

#### Option C: Tabbed Interface
```
[Classic Elegant] [Modern Refined] [Bold Statement]
[Selected outfit content]
```

### 3. Loading States

Update loading states to reflect the new structure:
```javascript
// Old loading message
"Searching for outfit..."

// New loading message  
"Generating 3 unique outfit variations..."
```

### 4. Error Handling

The error response structure remains the same:
```json
{
  "success": false,
  "error": "Error message",
  "timestamp": "2025-06-19T20:33:37.743864"
}
```

### 5. API Endpoints

The endpoints remain the same:
- **POST** `/search_outfit` - Search for outfits (updated response structure)
- **POST** `/parse_prompt` - Parse prompt only (now returns `outfit_variations` instead of `outfit_items`)
- **GET** `/health` - Health check (unchanged)

## Example API Usage

### Search for Outfits
```javascript
const searchOutfits = async (prompt) => {
  const response = await fetch('/search_outfit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt: prompt,
      top_results_per_item: 1,  // Default is now 1
      sort_by_price: true,
      price_order: 'asc'
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Handle 3 outfit variations
    console.log(`Found ${data.total_outfits} outfit variations`);
    data.outfits.forEach(outfit => {
      console.log(`Variation: ${outfit.variation_name}`);
      console.log(`Description: ${outfit.variation_description}`);
      console.log(`Items: ${outfit.items.length}`);
    });
  }
};
```

### Parse Prompt Only
```javascript
const parsePrompt = async (prompt) => {
  const response = await fetch('/parse_prompt', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt: prompt })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Now returns outfit_variations instead of outfit_items
    console.log(`Generated ${data.outfit_variations.length} variations`);
    data.outfit_variations.forEach(variation => {
      console.log(`Variation: ${variation.variation_name}`);
      console.log(`Description: ${variation.variation_description}`);
    });
  }
};
```

## Benefits of the New Structure

1. **More Variety**: Users get three different interpretations of their style request
2. **Better User Experience**: Each outfit is complete and cohesive
3. **Clearer Intent**: Variation names and descriptions help users understand the style differences
4. **Optimized Selection**: Only the best items are selected, reducing choice paralysis

## Migration Checklist

- [ ] Update frontend to handle 3 outfit variations instead of 1
- [ ] Display variation names and descriptions
- [ ] Update loading states and user messaging
- [ ] Test with new response structure
- [ ] Update any hardcoded expectations about number of outfits
- [ ] Consider UI layout changes to accommodate multiple outfits
- [ ] Update any analytics tracking for outfit interactions

## Testing

Test the new API with these example prompts:
- "old money summer vibe with deep autumn colors"
- "minimalist Scandinavian style with neutral tones"
- "streetwear aesthetic with bold colors"
- "business casual for a tech startup"

Each should return 3 distinct outfit variations with clear style differences. 