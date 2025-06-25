# AI Server - Database-Powered Outfit Search

This module provides AI-powered outfit search functionality that queries a Supabase database instead of scraping Zalando directly.

## Overview

The AI server now uses a pre-populated Supabase database for fast, reliable product searches. This provides:

- **Faster response times** - No web scraping delays
- **Reliable results** - Consistent data from your database
- **Better filtering** - Advanced color and material matching
- **Scalability** - Can handle multiple concurrent requests

## Features

### Database Search
- Search products by clothing type, color, material, and other filters
- Sort results by price (ascending or descending)
- Advanced color matching using extracted color data
- Material filtering with fuzzy matching

### AI-Powered Outfit Generation
- Parse natural language outfit descriptions
- Generate multiple outfit variations
- Intelligent product matching and recommendations

### REST API
- Flask-based web server
- CORS-enabled for frontend integration
- Comprehensive error handling and logging

## Setup

### Prerequisites
1. **Supabase Database**: Must have a populated `clothes_db` table
2. **Environment Variables**:
   ```bash
   export SUPABASE_KEY='your-supabase-anon-key'
   ```
3. **API Keys**: Add your OpenAI API key to `../keys.py`

### Installation
```bash
cd ai_server
pip install -r ../requirements.txt
```

## Usage

### Start the Server
```bash
python run_server.py
```

The server will start on `http://localhost:5000`

### API Endpoints

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Search Outfit
```bash
curl -X POST http://localhost:5000/search_outfit \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "minimalist summer outfit with neutral colors",
    "top_results_per_item": 2,
    "sort_by_price": true,
    "price_order": "asc"
  }'
```

#### Parse Prompt Only
```bash
curl -X POST http://localhost:5000/parse_prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "old money summer vibe with deep autumn colors"
  }'
```

## Testing

Run the test suite to verify everything is working:

```bash
python test_database_search.py
```

This will test:
- Database connection
- Single product search
- Outfit search
- AI prompt parsing

## Database Schema

The search functions expect a `clothes_db` table with the following structure:

```sql
CREATE TABLE clothes_db (
    id BIGSERIAL PRIMARY KEY,
    clothing_type TEXT,
    name TEXT,
    price TEXT,
    material TEXT,
    description TEXT,
    article_number TEXT,
    manufacturing_info TEXT,
    original_url TEXT UNIQUE,
    image_url TEXT,
    original_image_url TEXT,
    packshot_found BOOLEAN,
    dominant_color_hex TEXT,
    dominant_color_rgb TEXT,
    dominant_tone TEXT,
    dominant_hue TEXT,
    dominant_shade TEXT,
    overall_tone TEXT,
    overall_hue TEXT,
    overall_shade TEXT,
    color_count INTEGER,
    neutral_colors INTEGER,
    color_extraction_success BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Search Functions

### `search_database_products()`
Search for products in the database with filters.

```python
from search_function import search_database_products

results = search_database_products(
    clothing_type='sweaters',
    color='BLUE',
    filters={'material': 'linne'},
    max_items=10,
    sort_by_price=True,
    price_order='asc'
)
```

### `search_outfit()`
Search for multiple clothing items to create an outfit.

```python
from search_function import search_outfit

outfit_items = [
    {
        'clothing_type': 'sweaters',
        'color': 'BLUE',
        'max_items': 5
    },
    {
        'clothing_type': 'pants',
        'color': 'BLACK',
        'max_items': 5
    }
]

outfit_results = search_outfit(outfit_items, top_results_per_item=3)
```

### `OutfitPromptParser`
Parse natural language prompts into structured search parameters.

```python
from outfit_prompt_parser import OutfitPromptParser

parser = OutfitPromptParser(api_key)
outfit_response = parser.parse_outfit_prompt("minimalist summer outfit")
results = parser.search_outfit_from_prompt("minimalist summer outfit")
```

## Color Matching

The search function uses advanced color matching based on extracted color data:

- **Dominant colors**: Matches against `dominant_tone`, `dominant_hue`, `dominant_shade`
- **Overall colors**: Matches against `overall_tone`, `overall_hue`, `overall_shade`
- **Fuzzy matching**: Uses case-insensitive partial matching

## Material Filtering

Material filtering supports:
- Exact material names (e.g., 'linne', 'bomull')
- Partial matching with `%` wildcards
- Case-insensitive search

## Error Handling

The system includes comprehensive error handling:
- Database connection failures
- Invalid search parameters
- Missing environment variables
- API rate limiting

## Performance

- **Database queries**: Optimized with proper indexing
- **Caching**: Results are not cached (implement if needed)
- **Concurrent requests**: Flask handles multiple requests
- **Memory usage**: Minimal memory footprint

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check `SUPABASE_KEY` environment variable
   - Verify Supabase project URL
   - Ensure database table exists

2. **No Results Found**
   - Check if database has data for the requested clothing type
   - Verify color/material filters match available data
   - Try broader search criteria

3. **AI Parsing Errors**
   - Check OpenAI API key in `keys.py`
   - Verify API quota and rate limits
   - Check internet connection

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Caching**: Implement Redis caching for frequently searched items
- **Advanced filtering**: Add size, brand, and price range filters
- **Recommendations**: Implement collaborative filtering
- **Image search**: Add visual similarity search
- **Real-time updates**: WebSocket support for live updates 