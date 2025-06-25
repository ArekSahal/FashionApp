# FashionApp

A comprehensive Python application for AI-powered outfit search and fashion product discovery from Zalando.se. This application combines web scraping, natural language processing, and intelligent search to help users find perfect outfits using simple descriptions.

## 🚀 Features

### Core Features
- **🤖 AI-Powered Outfit Search**: Describe outfits in natural language and get structured recommendations
- **🌐 Flask Web Server**: RESTful API for outfit search with comprehensive endpoints
- **🔍 Smart Product Search**: Find the best matching products based on search terms and relevance scoring
- **📊 Zalando Product Scraping**: Scrape product information from Zalando.se with customizable filters
- **💰 Price Sorting**: Sort results by price in ascending or descending order
- **🎨 Comprehensive Filtering**: Support for colors, sizes, brands, materials, and custom search queries
- **📄 Pagination Handling**: Automatically handles pagination to fetch the requested number of items

### AI Features
- **Natural Language Processing**: Convert plain English descriptions into structured search parameters
- **Outfit Vision Generation**: AI creates detailed descriptions of envisioned outfits
- **Multi-Item Outfit Creation**: Search for complete outfits with multiple clothing pieces
- **Intelligent Parameter Mapping**: Automatically maps style descriptions to clothing types and filters

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd FashionApp
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Install Firefox WebDriver for Selenium:
   - Download Firefox WebDriver from: https://github.com/mozilla/geckodriver/releases
   - Add it to your system PATH or place it in the project directory

4. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or create a `keys.py` file:
```python
API_KEY = 'your-openai-api-key-here'
```

## 🏗️ Project Structure

The project is organized into two main modules:

```
FashionApp/
├── data_collection/           # Data scraping and database operations
│   ├── zalando_scraper.py     # Core scraping functionality
│   ├── color_extractor.py     # Color analysis and extraction
│   ├── supabase_db.py         # Database operations
│   ├── bulk_product_collector.py      # Automated bulk collection
│   ├── detailed_product_collector.py  # Detailed product collection
│   ├── zalando_exctractor/    # Additional extraction utilities
│   ├── run_collection.py      # Entry point for data collection
│   └── README.md              # Data collection documentation
│
├── ai_server/                 # AI server and prompt processing
│   ├── app.py                 # Flask web server with REST API
│   ├── outfit_prompt_parser.py # AI-powered outfit search
│   ├── search_function.py     # Smart search and matching
│   ├── run_server.py          # Entry point for AI server
│   └── README.md              # AI server documentation
│
├── keys.py                    # API key configuration
├── requirements.txt           # Python dependencies
├── README.md                  # This documentation
└── [Documentation files]      # Various README files
```

## 🚀 Quick Start

### 1. Data Collection (First Time Setup)
```bash
cd data_collection
python run_collection.py
```
Choose option 1 for bulk collection to populate your database with products.

### 2. Start AI Server
```bash
cd ai_server
python run_server.py
```
The server will start on `http://localhost:5000`

### 3. Use the API
```bash
curl -X POST http://localhost:5000/search_outfit \
  -H "Content-Type: application/json" \
  -d '{"prompt": "minimalist summer outfit", "top_results_per_item": 2}'
```

## 🌐 Web Server (Flask API)

The application includes a Flask web server that provides RESTful API endpoints for outfit search.

### Starting the Server

```bash
python app.py
```

The server runs on `http://localhost:5003` by default.

### Available Endpoints

#### 1. Health Check
```http
GET /health
```

Returns server status and parser readiness.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "parser_ready": true
}
```

#### 2. Search Outfits
```http
POST /search_outfit
```

Search for outfits using natural language descriptions.

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

#### 3. Parse Prompt Only
```http
POST /parse_prompt
```

Parse a prompt without searching for products (for testing/debugging).

**Request Body:**
```json
{
  "prompt": "old money summer vibe with deep autumn colors"
}
```

**Response:**
```json
{
  "success": true,
  "outfit_description": "A sophisticated summer outfit...",
  "outfit_items": [
    {
      "clothing_type": "shirts",
      "color": "BROWN",
      "filters": {"upper_material": "linne", "q": "short sleeve"}
    }
  ]
}
```

## 🤖 AI-Powered Outfit Search

The application uses OpenAI's GPT-4 to convert natural language descriptions into structured search parameters.

### Basic Usage

```python
from outfit_prompt_parser import OutfitPromptParser

# Initialize the parser
parser = OutfitPromptParser(api_key="your-openai-api-key")

# Search for an outfit using natural language
results = parser.search_outfit_from_prompt(
    prompt="old money summer vibe with deep autumn colors",
    top_results_per_item=3,
    sort_by_price=True,
    price_order='asc'
)

# Display results
for clothing_type, products in results.items():
    print(f"\n{clothing_type}:")
    for product in products:
        print(f"  - {product['name']} - {product['price']}")
```

### Convenience Function

```python
from outfit_prompt_parser import search_outfit_with_ai_prompt

results = search_outfit_with_ai_prompt(
    api_key="your-openai-api-key",
    prompt="minimalist Scandinavian style with neutral tones",
    top_results_per_item=2
)
```

### Interactive Mode

Run the example script in interactive mode:

```bash
python example_ai_outfit_search.py --interactive
```

This will let you input outfit descriptions and see results in real-time.

### Example Prompts

Here are some example prompts you can try:

- **"old money summer vibe with deep autumn colors"**
- **"minimalist Scandinavian style with neutral tones"**
- **"streetwear aesthetic with bold colors"**
- **"business casual for a tech startup"**
- **"vintage 90s grunge look"**
- **"elegant evening wear for a formal event"**
- **"cozy winter outfit with warm earth tones"**
- **"athletic wear for running and gym"**

## 🔍 Core Modules

### 1. Zalando Scraper (`zalando_scraper.py`)

The main scraping module that handles fetching products from Zalando.se.

#### Key Functions

##### `get_zalando_products(clothing_type, filters=None, max_items=5)`

Scrapes product information from Zalando.se based on clothing type and filters.

**Parameters:**
- `clothing_type` (str): Type of clothing from the available options
- `filters` (dict, optional): Dictionary of filters to apply
- `max_items` (int): Maximum number of products to return (default: 5)

**Returns:**
- `list`: List of dictionaries containing product information

**Example:**
```python
from zalando_scraper import get_zalando_products

# Get 10 blue shirts in size M
products = get_zalando_products('shirts', {
    'color': 'BLUE',
    'size': 'M'
}, max_items=10)
```

##### `build_zalando_url(clothing_type, base_category='herrklader', filters=None)`

Builds a Zalando URL with filters for web scraping.

**Parameters:**
- `clothing_type` (str): Type of clothing from CLOTHING_TYPES mapping
- `base_category` (str): Base category (default: 'herrklader')
- `filters` (dict): Dictionary of filters

**Returns:**
- `str`: Complete Zalando URL with filters

#### Available Clothing Types

The following clothing types are supported:

| Type | URL Segment | Description |
|------|-------------|-------------|
| `t_shirts` | man-klader-overdelar | T-shirts |
| `shirts` | man-klader-skjortor | Shirts |
| `sweaters` | man-klader-trojor | Sweaters |
| `pants` | man-klader-byxor | Pants |
| `jeans` | man-klader-jeans | Jeans |
| `shorts` | man-klader-byxor-shorts | Shorts |
| `jackets` | man-klader-jackor | Jackets |
| `knitwear` | man-klader-stickat | Knitwear |
| `sportswear` | man-sport-klader | Sportswear |
| `tracksuits` | man-klader-tracksuits | Tracksuits |
| `suits` | man-klader-kostymer | Suits |
| `coats` | man-klader-rockar | Coats |
| `underwear` | man-klader-underklader | Underwear |
| `swimwear` | man-klader-badmode | Swimwear |
| `loungewear` | man-klader-underklader-nattklader | Loungewear |
| `outlet` | herrklader-rea | Outlet items |

#### Available Colors

The following colors are supported (case-insensitive):

| Color | URL Value | Color | URL Value |
|-------|-----------|-------|-----------|
| BLACK | svart | GREEN | groen |
| BROWN | brun | OLIVE | oliv |
| BEIGE | beige | YELLOW | gul |
| GRAY | gra | RED | roed |
| WHITE | vit | ORANGE | orange |
| BLUE | bla | GOLD | guld |
| PETROL | petrol | PINK | rosa |
| TURQUOISE | turkos | SILVER | silver |
| | | PURPLE | lila |

#### Available Materials

The following materials are supported for filtering (case-insensitive):

| Material | Description |
|----------|-------------|
| bomull | Cotton |
| bomullsflanell | Cotton flannel |
| chiffon | Chiffon |
| fjäder | Feather |
| fleece | Fleece |
| hardshell | Hardshell |
| jeans | Denim |
| jersey | Jersey |
| kabelstickad | Cable knit |
| kashmir | Cashmere |
| knitted_fabric | Knitted fabric |
| linne | Linen |
| manchester | Corduroy |
| meshtyg | Mesh fabric |
| mohair | Mohair |
| polyester | Polyester |
| pure_cashmere | Pure cashmere |
| pure_cotton | Pure cotton |
| pure_linen | Pure linen |
| pure_lyocell | Pure lyocell |
| pure_silk | Pure silk |
| pure_viscose | Pure viscose |
| pure_wool | Pure wool |
| ribbad | Ribbed |
| satin | Satin |
| sequins | Sequins |
| siden | Silk |
| skinn | Leather |
| skinnimitation | Faux leather |
| softshell | Softshell |
| spets | Lace |
| syntetiskt---material | Synthetic material |
| textil | Textile |
| ull | Wool |
| virkad | Crocheted |
| viskos | Viscose |
| övrigt | Other |

#### Filter Parameters

The `filters` parameter accepts a dictionary with the following keys:

- `color`: One of the available colors (e.g., 'BLACK', 'GREEN')
- `size`: Size of the clothing (e.g., 'M', 'L', 'XL')
- `brand`: Brand name
- `material` or `upper_material`: One of the available materials (e.g., 'linne', 'bomull', 'polyester'). Both are accepted, but `upper_material` is used in the URL.
- `q`: Search query for specific clothing types (e.g., 'chino', 'box-shirt', 'short sleeve', 'crewneck')
- Additional filters can be added based on Zalando's URL parameters

**Note**: Materials must be specified using the exact names from the available materials list above.
**Note**: Use the `q` parameter for specific clothing types, not style descriptors (e.g., use 'chino' not 'casual').
**Note**: Materials are automatically converted to `upper_material` in the URL for proper Zalando filtering.

#### Return Value Structure

Each product in the returned list contains:

```python
{
    'name': str,              # Product name
    'url': str,              # Product URL
    'image_url': str,        # Main product image URL
    'secondary_image_url': str,  # Secondary product image URL (if available)
    'price': str             # Product price in SEK
}
```

### 2. Search Function (`search_function.py`)

The smart search module that finds the best matching products based on search terms and relevance scoring.

#### Key Functions

##### `search_zalando_products(clothing_type, filters=None, search_terms=None, max_items=10, color=None, sort_by_price=False, price_order='asc')`

Searches Zalando products with filters and finds the best matches based on search terms.

**Parameters:**
- `clothing_type` (str): Type of clothing (e.g., 'sweaters', 't_shirts', 'shirts')
- `filters` (dict, optional): Dictionary of filters to apply
- `search_terms` (str or list, optional): Terms to search for in product names
- `max_items` (int, optional): Maximum number of products to return (default: 10)
- `color` (str, optional): Color of the item (convenience parameter)
- `sort_by_price` (bool, optional): Whether to sort results by price (default: False)
- `price_order` (str, optional): Sort order for price ('asc' or 'desc', default: 'asc')

**Returns:**
- `list`: List of dictionaries containing the best matching products, sorted by relevance and optionally by price

**Example:**
```python
from search_function import search_zalando_products

# Search for blue crewneck sweaters
results = search_zalando_products(
    clothing_type='sweaters',
    color='BLUE',
    search_terms='crewneck',
    max_items=15,
    sort_by_price=True,
    price_order='asc'
)
```

##### `extract_price(price_str)`

Extracts numeric price from price string.

**Parameters:**
- `price_str` (str): Price string from Zalando (e.g., '499,00 kr', '1 299,00 kr')

**Returns:**
- `float`: Extracted price value, or float('inf') if price is not available

#### Relevance Scoring

The search function uses a sophisticated scoring system to find the best matches:

1. **Exact Matches**: Terms that appear exactly in the product name get the highest score
2. **Partial Matches**: Uses sequence matching to find similar terms with high similarity (>0.8)
3. **Normalization**: Scores are normalized by the number of search terms
4. **Price Integration**: Can sort by price in addition to relevance

#### Return Value Structure

Each product in the returned list contains:

```python
{
    'name': str,              # Product name
    'url': str,              # Product URL
    'image_url': str,        # Main product image URL
    'secondary_image_url': str,  # Secondary product image URL
    'price': str,            # Product price in SEK
    'relevance_score': float, # Relevance score (0.0 to 1.0)
    'price_value': float     # Numeric price value for sorting
}
```

### 3. Outfit Prompt Parser (`outfit_prompt_parser.py`)

The AI-powered module that converts natural language descriptions into structured search parameters.

#### Key Functions

##### `parse_outfit_prompt(prompt, max_items_per_category=50)`

Parses a natural language outfit description into structured search parameters.

**Parameters:**
- `prompt` (str): Natural language description (e.g., "old money summer vibe with deep autumn colors")
- `max_items_per_category` (int): Maximum items to search per clothing category

**Returns:**
- `dict`: Dictionary containing outfit description and structured outfit items

##### `search_outfit_from_prompt(prompt, top_results_per_item=3, sort_by_price=True, price_order='asc')`

Searches for complete outfits based on a natural language prompt.

**Parameters:**
- `prompt` (str): Natural language outfit description
- `top_results_per_item` (int): Number of top results per clothing item
- `sort_by_price` (bool): Whether to sort by price
- `price_order` (str): Price sort order ('asc' or 'desc')

**Returns:**
- `dict`: Dictionary mapping clothing types to product lists

## 📖 Usage Examples

### Basic Product Scraping

```python
from zalando_scraper import get_zalando_products

# Get 5 black t-shirts
products = get_zalando_products('t_shirts', {
    'color': 'BLACK'
}, max_items=5)

# Get 10 blue jeans with specific material
products = get_zalando_products('jeans', {
    'color': 'BLUE',
    'upper_material': 'denim'
}, max_items=10)
```

### Smart Product Search

```python
from search_function import search_zalando_products

# Search for crewneck sweaters
results = search_zalando_products(
    clothing_type='sweaters',
    search_terms='crewneck',
    max_items=20
)

# Search for blue chinos with price sorting
results = search_zalando_products(
    clothing_type='pants',
    filters={'q': 'chinos'},
    color='BLUE',
    search_terms='chino',
    max_items=15,
    sort_by_price=True,
    price_order='asc'
)
```

### AI-Powered Outfit Search

```python
from outfit_prompt_parser import OutfitPromptParser

# Initialize parser
parser = OutfitPromptParser(api_key="your-openai-api-key")

# Search for complete outfit
results = parser.search_outfit_from_prompt(
    prompt="minimalist Scandinavian style with neutral tones",
    top_results_per_item=3,
    sort_by_price=True,
    price_order='asc'
)

# Display results
for clothing_type, products in results.items():
    print(f"\n{clothing_type}:")
    for product in products:
        print(f"  - {product['name']} - {product['price']}")
```

### Advanced Filtering

```python
# Complex search with multiple filters
results = search_zalando_products(
    clothing_type='shirts',
    filters={
        'color': 'WHITE',
        'size': 'M',
        'upper_material': 'linne',
        'q': 'randig'
    },
    search_terms='linne shirt',
    max_items=25,
    sort_by_price=True,
    price_order='desc'
)
```

### Using the Web API

```bash
# Health check
curl http://localhost:5003/health

# Search for outfits
curl -X POST http://localhost:5003/search_outfit \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "old money summer vibe with deep autumn colors",
    "top_results_per_item": 3,
    "sort_by_price": true,
    "price_order": "asc"
  }'

# Parse prompt only
curl -X POST http://localhost:5003/parse_prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "minimalist Scandinavian style"
  }'
```

## 🔧 Error Handling

The application includes comprehensive error handling:

- **Invalid Clothing Type**: Raises `ValueError` with available options
- **Invalid Color**: Raises `ValueError` with available colors
- **No Products Found**: Raises `ValueError` when no items match criteria
- **Network Issues**: Gracefully handles connection problems
- **Missing Elements**: Continues processing when individual elements are not found
- **API Errors**: Handles OpenAI API errors gracefully
- **Invalid JSON**: Validates AI responses and provides clear error messages

## ⚡ Performance Considerations

- **Rate Limiting**: Includes 5-second delays between page loads to respect Zalando's servers
- **Pagination**: Automatically handles pagination to fetch requested number of items
- **Progress Tracking**: Uses progress bars to show scraping and scoring progress
- **Memory Efficiency**: Processes products incrementally to manage memory usage
- **Caching**: AI responses can be cached to reduce API calls
- **Concurrent Processing**: Web server supports threaded requests

## 📦 Dependencies

- **selenium**: Web scraping and browser automation
- **openai**: OpenAI API integration for AI-powered search
- **requests**: HTTP requests for image downloading
- **tqdm**: Progress bars for user feedback
- **difflib**: String similarity matching for search terms
- **flask**: Web server framework for REST API

## 🌐 Browser Requirements

- **Firefox**: Required for Selenium WebDriver
- **GeckoDriver**: Firefox WebDriver executable
- **Headless Mode**: Configured to run without GUI for server environments

## 🎯 Tips for Better Results

### AI-Powered Search
1. **Be Specific**: "elegant business suit" works better than "nice clothes"
2. **Include Colors**: "blue jeans" is more specific than just "jeans"
3. **Mention Style**: "vintage style" or "modern minimalist" helps the AI
4. **Consider Season**: "summer casual" or "winter warm" provides context
5. **Use Style Terms**: "old money", "streetwear", "business casual", etc.

### Traditional Search
1. **Use Specific Terms**: "crewneck" instead of "sweater"
2. **Combine Filters**: Use color + material + specific type
3. **Leverage q Parameter**: For specific clothing types like "chino", "box-shirt"
4. **Sort by Price**: Use price sorting for budget-conscious searches

## 🐛 Troubleshooting

### Common Issues

1. **WebDriver Not Found**: Ensure GeckoDriver is installed and in PATH
2. **No Products Found**: Check if filters are too restrictive
3. **Network Errors**: Verify internet connection and Zalando accessibility
4. **Memory Issues**: Reduce `max_items` for large searches
5. **API Key Issues**: Verify OpenAI API key is set correctly
6. **Server Not Starting**: Check if port 5003 is available

### Debug Mode

To see detailed logging, the application includes:
- Progress bars and status messages
- Detailed server logs in `outfit_server.log`
- AI response validation and error messages
- Network request tracking

### Getting Help

If you encounter issues:
1. Check the error messages for specific details
2. Verify your API key is working
3. Try simpler prompts first
4. Check that all dependencies are installed correctly
5. Review the server logs for detailed error information

## 📝 Notes

- The application is designed for Swedish Zalando (zalando.se)
- All prices are in SEK (Swedish Krona)
- The scraper respects website terms by including delays between requests
- Product availability may vary based on Zalando's inventory
- The application is optimized for men's clothing but can be adapted for other categories
- AI features require an active OpenAI API key with sufficient credits

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here] 