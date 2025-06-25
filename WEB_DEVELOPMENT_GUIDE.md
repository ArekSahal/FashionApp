# FashionApp API - Web Development Integration Guide

## Quick Start

### 1. API Base URL
```
http://localhost:5003
```

### 2. Start the API Server
```bash
cd FashionApp
python app.py
```

## API Endpoints

### Health Check
**GET** `/health`

Check if the API is running and ready.

```javascript
// Example response
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "parser_ready": true
}
```

### Search Outfits
**POST** `/search_outfit`

Search for complete outfits using natural language descriptions.

**Request Body:**
```json
{
  "prompt": "old money summer vibe with deep autumn colors",
  "top_results_per_item": 3,
  "sort_by_price": true,
  "price_order": "asc"
}
```

**Response:**
```json
{
  "success": true,
  "outfit_description": "A sophisticated summer outfit with an old money aesthetic...",
  "outfits": [
    {
      "outfit_id": 1,
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
    }
  ],
  "total_outfits": 1,
  "total_products": 3,
  "search_metadata": {
    "prompt": "old money summer vibe with deep autumn colors",
    "top_results_per_item": 3,
    "sort_by_price": true,
    "price_order": "asc",
    "clothing_types_searched": ["shirts", "pants"]
  }
}
```

### Parse Prompt Only
**POST** `/parse_prompt`

Parse a prompt without searching for products (for testing/debugging).

**Request Body:**
```json
{
  "prompt": "minimalist Scandinavian style"
}
```

## Frontend Integration Examples

### React/JavaScript Example

```javascript
class FashionAppAPI {
  constructor(baseURL = 'http://localhost:5003') {
    this.baseURL = baseURL;
  }

  async healthCheck() {
    const response = await fetch(`${this.baseURL}/health`);
    return response.json();
  }

  async searchOutfit(prompt, options = {}) {
    const {
      top_results_per_item = 3,
      sort_by_price = true,
      price_order = 'asc'
    } = options;

    const response = await fetch(`${this.baseURL}/search_outfit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        top_results_per_item,
        sort_by_price,
        price_order
      })
    });

    return response.json();
  }

  async parsePrompt(prompt) {
    const response = await fetch(`${this.baseURL}/parse_prompt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt })
    });

    return response.json();
  }
}

// Usage
const api = new FashionAppAPI();

// Search for outfits
const searchOutfit = async () => {
  try {
    const result = await api.searchOutfit(
      "old money summer vibe with deep autumn colors",
      { top_results_per_item: 5, sort_by_price: true }
    );
    
    if (result.success) {
      console.log('Outfit description:', result.outfit_description);
      result.outfits.forEach(outfit => {
        outfit.items.forEach(item => {
          console.log(`${item.clothing_type}: ${item.name} - ${item.price}`);
        });
      });
    }
  } catch (error) {
    console.error('Search failed:', error);
  }
};
```

### React Component Example

```jsx
import React, { useState } from 'react';

const OutfitSearch = () => {
  const [prompt, setPrompt] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5003/search_outfit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          top_results_per_item: 3,
          sort_by_price: true,
          price_order: 'asc'
        })
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe your outfit (e.g., 'old money summer vibe')"
      />
      <button onClick={handleSearch} disabled={loading}>
        {loading ? 'Searching...' : 'Search Outfit'}
      </button>
      
      {results && results.success && (
        <div>
          <h3>AI Description: {results.outfit_description}</h3>
          {results.outfits.map(outfit => (
            <div key={outfit.outfit_id}>
              {outfit.items.map(item => (
                <div key={item.url}>
                  <img src={item.image_url} alt={item.name} />
                  <h4>{item.name}</h4>
                  <p>{item.price}</p>
                  <a href={item.url} target="_blank" rel="noopener noreferrer">
                    View on Zalando
                  </a>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

### Vue.js Example

```vue
<template>
  <div>
    <input v-model="prompt" placeholder="Describe your outfit" />
    <button @click="searchOutfit" :disabled="loading">
      {{ loading ? 'Searching...' : 'Search' }}
    </button>
    
    <div v-if="results && results.success">
      <h3>{{ results.outfit_description }}</h3>
      <div v-for="outfit in results.outfits" :key="outfit.outfit_id">
        <div v-for="item in outfit.items" :key="item.url" class="product-card">
          <img :src="item.image_url" :alt="item.name" />
          <h4>{{ item.name }}</h4>
          <p>{{ item.price }}</p>
          <a :href="item.url" target="_blank">View on Zalando</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      prompt: '',
      results: null,
      loading: false
    };
  },
  methods: {
    async searchOutfit() {
      this.loading = true;
      try {
        const response = await fetch('http://localhost:5003/search_outfit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: this.prompt,
            top_results_per_item: 3,
            sort_by_price: true,
            price_order: 'asc'
          })
        });
        
        this.results = await response.json();
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

## Best Practices

### 1. Error Handling
```javascript
const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    console.error('API Error:', error.response.status, error.response.data);
  } else if (error.request) {
    // Network error
    console.error('Network Error:', error.request);
  } else {
    // Other error
    console.error('Error:', error.message);
  }
};
```

### 2. Loading States
Always implement loading states for better UX:
```javascript
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

// In your API call
setLoading(true);
setError(null);
try {
  // API call
} catch (err) {
  setError(err.message);
} finally {
  setLoading(false);
}
```

### 3. CORS Configuration
CORS is already configured in the Flask server to allow all origins. If you need to restrict origins for production, update the CORS configuration in `app.py`:

```python
# Current configuration (allows all origins)
CORS(app, resources={r"/*": {"origins": "*"}})

# For production, restrict to specific domains:
CORS(app, resources={r"/*": {"origins": ["https://yourdomain.com", "http://localhost:3000"]}})
```

The server automatically adds CORS headers to all responses, so no additional configuration is needed on the frontend.

### 4. Rate Limiting
The API includes built-in delays, but implement client-side rate limiting:
```javascript
class RateLimitedAPI {
  constructor() {
    this.lastCall = 0;
    this.minInterval = 1000; // 1 second
  }

  async makeRequest(url, options) {
    const now = Date.now();
    const timeSinceLastCall = now - this.lastCall;
    
    if (timeSinceLastCall < this.minInterval) {
      await new Promise(resolve => 
        setTimeout(resolve, this.minInterval - timeSinceLastCall)
      );
    }
    
    this.lastCall = Date.now();
    return fetch(url, options);
  }
}
```

## Prompt Examples for Testing

Use these prompts to test the API:

- **"old money summer vibe with deep autumn colors"**
- **"minimalist Scandinavian style with neutral tones"**
- **"streetwear aesthetic with bold colors"**
- **"business casual for a tech startup"**
- **"vintage 90s grunge look"**
- **"elegant evening wear for a formal event"**
- **"cozy winter outfit with warm earth tones"**
- **"athletic wear for running and gym"**

## Response Data Structure

### Successful Response
```json
{
  "success": true,
  "outfit_description": "AI-generated description",
  "outfits": [
    {
      "outfit_id": 1,
      "items": [
        {
          "clothing_type": "shirts",
          "name": "Product Name",
          "price": "499,00 kr",
          "url": "https://www.zalando.se/...",
          "image_url": "https://img01.ztat.net/...",
          "secondary_image_url": "https://img01.ztat.net/..."
        }
      ]
    }
  ],
  "total_outfits": 1,
  "total_products": 3,
  "search_metadata": {
    "prompt": "original prompt",
    "top_results_per_item": 3,
    "sort_by_price": true,
    "price_order": "asc",
    "clothing_types_searched": ["shirts", "pants"]
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "details": "Additional error details"
}
```

## Environment Setup

### Development
```bash
# Install dependencies (including flask-cors for CORS support)
cd FashionApp
pip install -r requirements.txt

# Start the API server
python app.py

# The API will be available at http://localhost:5003
```

### Production Considerations
- Deploy the Flask app to your preferred hosting service
- Update the base URL in your frontend code
- Implement proper error handling and logging
- Consider implementing caching for frequently requested outfits
- Monitor API usage and performance

## Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure CORS is enabled on the Flask server
2. **Connection Refused**: Verify the API server is running on port 5003
3. **Timeout Errors**: The API can take 10-30 seconds for complex searches
4. **No Results**: Try simpler prompts or check if Zalando has products matching the criteria

### Debug Mode
Enable detailed logging by checking the server console output and `outfit_server.log` file in the FashionApp directory. 