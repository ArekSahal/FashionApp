from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlencode
import time
import requests
import os
from datetime import datetime
from tqdm import tqdm

# Mapping of clothing types to their URL segments
CLOTHING_TYPES = {
    't_shirts': 'man-klader-overdelar',
    'shirts': 'man-klader-skjortor',
    'sweaters': 'man-klader-trojor',
    'pants': 'man-klader-byxor',
    'jeans': 'man-klader-jeans',
    'shorts': 'man-klader-byxor-shorts',
    'jackets': 'man-klader-jackor',
    'knitwear': 'man-klader-stickat',
    'sportswear': 'man-sport-klader',
    'tracksuits': 'man-klader-tracksuits',
    'suits': 'man-klader-kostymer',
    'coats': 'man-klader-rockar',
    'underwear': 'man-klader-underklader',
    'swimwear': 'man-klader-badmode',
    'loungewear': 'man-klader-underklader-nattklader',
    'outlet': 'herrklader-rea'
}

# Available colors and their URL mappings
COLORS = {
    'BLACK': 'svart',
    'BROWN': 'brun',
    'BEIGE': 'beige',
    'GRAY': 'gra',
    'WHITE': 'vit',
    'BLUE': 'bla',
    'PETROL': 'petrol',
    'TURQUOISE': 'turkos',
    'GREEN': 'groen',
    'OLIVE': 'oliv',
    'YELLOW': 'gul',
    'RED': 'roed',
    'ORANGE': 'orange',
    'GOLD': 'guld',
    'PINK': 'rosa',
    'SILVER': 'silver',
    'PURPLE': 'lila'
}

# Available materials for URL filtering
MATERIALS = [
    "bomull",
    "bomullsflanell",
    "chiffon",
    "fjäder",
    "fleece",
    "hardshell",
    "jeans",
    "jersey",
    "kabelstickad",
    "kashmir",
    "knitted_fabric",
    "linne",
    "manchester",
    "meshtyg",
    "mohair",
    "polyester",
    "pure_cashmere",
    "pure_cotton",
    "pure_linen",
    "pure_lyocell",
    "pure_silk",
    "pure_viscose",
    "pure_wool",
    "ribbad",
    "satin",
    "sequins",
    "siden",
    "skinn",
    "skinnimitation",
    "softshell",
    "spets",
    "syntetiskt---material",
    "textil",
    "ull",
    "virkad",
    "viskos",
    "övrigt"
]

def validate_color(color):
    """
    Validate and convert color to URL format
    
    Args:
        color (str): Color to validate (case insensitive)
    
    Returns:
        str: Validated color in URL format, or empty string if invalid
    
    Raises:
        ValueError: If color is not in COLORS mapping
    """
    if not color:
        return ''
        
    color_upper = color.upper()
    if color_upper not in COLORS:
        raise ValueError(f"Invalid color. Must be one of: {', '.join(COLORS.keys())}")
    
    return COLORS[color_upper]

def validate_material(material):
    """
    Validate and return material in URL format
    
    Args:
        material (str): Material to validate (case insensitive)
    
    Returns:
        str: Validated material in URL format, or empty string if invalid
    
    Raises:
        ValueError: If material is not in MATERIALS list
    """
    if not material:
        return ''
        
    material_lower = material.lower()
    if material_lower not in MATERIALS:
        raise ValueError(f"Invalid material. Must be one of: {', '.join(MATERIALS)}")
    
    return material_lower

def build_zalando_url(clothing_type, base_category='herrklader', filters=None):
    """
    Build a Zalando URL with filters, starting with clothing type
    
    Args:
        clothing_type (str): Type of clothing from CLOTHING_TYPES mapping
        base_category (str): Base category (e.g., 'herrklader', 'damklader'). Defaults to 'herrklader'
        filters (dict): Dictionary of filters where:
            - key: filter name (e.g., 'brand', 'size', 'upper_material', 'q' for search query)
            - value: filter value or list of values
            Empty values (None, '', [], etc.) will be skipped
    
    Returns:
        str: Complete Zalando URL with filters
    
    Raises:
        ValueError: If clothing_type is not in CLOTHING_TYPES or color is not in COLORS
    """
    if clothing_type not in CLOTHING_TYPES:
        raise ValueError(f"Invalid clothing type. Must be one of: {', '.join(CLOTHING_TYPES.keys())}")
    
    # Determine the base URL based on clothing type
    base_url = f"https://www.zalando.se/{CLOTHING_TYPES[clothing_type]}/"
    
    if not filters:
        return base_url
    
    # Create a copy of filters to modify
    processed_filters = filters.copy()
    
    # Handle search query separately if present
    search_query = processed_filters.pop('q', None)
    
    # Validate and convert color if present
    if 'color' in processed_filters:
        processed_filters['color'] = validate_color(processed_filters['color'])
    
    # Validate and convert material if present (only if upper_material is not present)
    if 'material' in processed_filters and 'upper_material' not in processed_filters:
        processed_filters['material'] = validate_material(processed_filters['material'])
        # Convert material to upper_material for URL
        processed_filters['upper_material'] = processed_filters.pop('material')
    
    # Validate and convert upper_material if present
    if 'upper_material' in processed_filters:
        processed_filters['upper_material'] = validate_material(processed_filters['upper_material'])
    
    # Convert filters to URL format, skipping empty values
    url_parts = []
    for key, value in processed_filters.items():
        # Skip if value is None, empty string, or empty list
        if value is None or value == '' or (isinstance(value, list) and len(value) == 0):
            continue
            
        if isinstance(value, list):
            # Filter out any empty values from the list
            value = [v for v in value if v is not None and v != '']
            if not value:  # Skip if list is empty after filtering
                continue
            # Join multiple values with dots
            value = '.'.join(value)
        url_parts.append(f"{key}={value}")
    
    # Add search query if present
    if search_query:
        url_parts.append(f"q={search_query}")
    
    # If no valid filters, return base URL
    if not url_parts:
        return base_url
        
    # Join all filter parts with '&'
    filter_string = '&'.join(url_parts)
    
    return f"{base_url}?{filter_string}"

def download_image(url, folder, filename):
    """
    Download an image from a URL and save it to the specified folder
    
    Args:
        url (str): URL of the image to download
        folder (str): Folder to save the image in
        filename (str): Name to save the file as
    
    Returns:
        str: Path to the saved image, or None if download failed
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Create folder if it doesn't exist
        os.makedirs(folder, exist_ok=True)
        
        # Save the image
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return filepath
    except Exception as e:
        tqdm.write(f"Error downloading image {url}: {str(e)}")
        return None

def normalize_zalando_url(url):
    """
    Normalize Zalando URL to handle different formats of the same filters
    
    Args:
        url (str): URL to normalize
    
    Returns:
        dict: Dictionary of filters extracted from the URL
    """
    # Extract the base URL and filter part
    if '?' in url:
        base, filter_part = url.split('?', 1)
    else:
        base = url
        filter_part = ''
    
    filters = {}
    
    # Handle format 1: ?color=groen&size=M&upper_material=linne
    if filter_part:
        for param in filter_part.split('&'):
            if '=' in param:
                key, value = param.split('=')
                filters[key] = value
    
    # Handle format 2: _groen_Storlek-M/?upper_material=linne
    if '_' in base:
        # Extract color from _color_ format
        color_parts = base.split('_')
        if len(color_parts) >= 2:
            filters['color'] = color_parts[1]
    
    # Extract size from Storlek-X format
    if 'Storlek-' in base:
        size_part = base.split('Storlek-')[1].split('/')[0]
        filters['size'] = size_part
    
    return filters

def are_urls_equivalent(url1, url2):
    """
    Check if two Zalando URLs represent the same filters
    
    Args:
        url1 (str): First URL to compare
        url2 (str): Second URL to compare
    
    Returns:
        bool: True if URLs represent the same filters
    """
    filters1 = normalize_zalando_url(url1)
    filters2 = normalize_zalando_url(url2)
    
    # Compare the filter dictionaries
    return filters1 == filters2

def get_zalando_products(clothing_type, filters=None, max_items=5):
    """
    Get a list of products from Zalando based on clothing type and filters.
    Handles pagination to fetch products across multiple pages if needed.
    
    Args:
        clothing_type (str): Type of clothing from CLOTHING_TYPES mapping
        filters (dict): Dictionary of filters (e.g., {
            'color': 'GREEN',
            'size': 'M',
            'q': 'search term',  # Optional search query
            'material': 'linne'
        })
        max_items (int): Maximum number of products to return (default: 5)
    
    Returns:
        list: List of dictionaries containing product information:
            {
                'name': str,          # Product name
                'url': str,           # Product URL
                'image_url': str,     # Main product image URL
                'secondary_image_url': str,  # Secondary product image URL (if available)
                'price': str          # Product price in SEK
            }
    
    Raises:
        ValueError: If clothing_type is invalid or no products found
    """
    options = Options()
    # Add headless mode options
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Firefox(options=options)
    products = []
    current_page = 1
    last_url = None
    
    try:
        # Create progress bar for overall product fetching
        pbar = tqdm(total=max_items, desc="Fetching products", unit="product")
        
        while len(products) < max_items:
            # Build and access the URL with page number
            url = build_zalando_url(clothing_type, 'herrklader', filters)
            if current_page > 1:
                # Add page parameter to URL
                url = f"{url}{'&' if '?' in url else '?'}p={current_page}"
            
            tqdm.write(f"Fetching page {current_page}")
            
            # Store the URL we're trying to access
            target_url = url
            
            driver.get(url)
            time.sleep(5)  # Wait for content to load
            
            # Get the actual URL after any redirects
            current_url = driver.current_url
            
            # Check if we got redirected to a different page than intended
            # or if we're back to a previous page (indicating no more results)
            if last_url and (current_url == last_url or 'p=' not in current_url):
                tqdm.write("No more pages available or reached end of results")
                break
                
            # Check if we got redirected to a different page than intended
            if current_page > 1 and 'p=' not in current_url:
                tqdm.write("Got redirected to first page, no more results available")
                break
            
            last_url = current_url
            
            # Find product items
            li_items = driver.find_elements(By.CSS_SELECTOR, 'li.QjLAB7._75qWlu.iOzucJ')
            if not li_items:
                if current_page == 1:
                    raise ValueError("No items found matching the specified criteria")
                break  # No more items on this page, stop pagination
            
            # Process each item
            items_processed = 0
            for item_index in range(len(li_items)):
                if len(products) >= max_items:
                    break
                
                # Use the safer method to get product information
                product_info = safe_get_product_info(driver, item_index)
                if product_info is None:
                    tqdm.write(f"Failed to get product info for item {item_index}, skipping")
                    continue
                
                try:
                    # Add product directly without people detection (that's handled in get_zalando_products_with_clean_images)
                    products.append({
                        'name': product_info['name'],
                        'url': product_info['url'],
                        'image_url': product_info['main_img_url'],
                        'secondary_image_url': product_info['secondary_img_url'],
                        'price': product_info['price']
                    })
                    
                    items_processed += 1
                    # Update progress bar
                    pbar.update(1)
                    
                except Exception as e:
                    product_name = product_info['name'] if product_info else "Unknown Product"
                    tqdm.write(f"Error processing product {product_name}: {str(e)}")
                    continue
            
            # Check if there's a next page
            try:
                next_page_button = driver.find_element(By.CSS_SELECTOR, 'a[data-testid="pagination-next"]')
                if not next_page_button.is_enabled():
                    tqdm.write("Next page button is disabled")
                    break  # No more pages
                current_page += 1
            except NoSuchElementException:
                tqdm.write("No next page button found")
                break  # No next page button found
        
        pbar.close()
        return products
        
    finally:
        driver.quit()

def find_packshot_image(product_url, driver):
    """
    Follow a product link and find the first image with "filter=packshot" in the URL
    
    Args:
        product_url (str): URL of the product page
        driver: Selenium WebDriver instance
    
    Returns:
        str: URL of the first image with "filter=packshot", or None if not found
    """
    try:
        # Navigate to product page
        driver.get(product_url)
        time.sleep(3)  # Wait for content to load
        
        # Find all images on the page
        image_elements = driver.find_elements(By.CSS_SELECTOR, 'img')
        
        if not image_elements:
            tqdm.write("No images found on the page")
            return None
        
        tqdm.write(f"Found {len(image_elements)} images to check")
        
        # Look for images with packshot filters in the URL
        packshot_patterns = [
            'filter=packshot',
            'filter=packshot_',
            'packshot',
            'product-shot',
            'product_image'
        ]
        
        for i, img_element in enumerate(image_elements):
            try:
                img_url = img_element.get_attribute('src')
                
                if not img_url or img_url.startswith('data:'):
                    continue
                
                # Check if URL contains any packshot pattern
                for pattern in packshot_patterns:
                    if pattern in img_url.lower():
                        tqdm.write(f"✅ Found packshot image with pattern '{pattern}': {img_url}")
                        return img_url
                    
            except Exception as e:
                tqdm.write(f"Error checking image {i+1}: {str(e)}")
                continue
        
        tqdm.write("No packshot image found")
        return None
        
    except Exception as e:
        tqdm.write(f"Error finding packshot image: {str(e)}")
        return None

def safe_get_product_info(driver, item_index, max_retries=3):
    """
    Safely extract product information from a list item with retry mechanism
    
    Args:
        driver: Selenium WebDriver instance
        item_index (int): Index of the item to process
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        dict: Product information or None if failed
    """
    for attempt in range(max_retries):
        try:
            # Wait for elements to be present
            wait = WebDriverWait(driver, 10)
            
            # Try multiple possible selectors for product items
            selectors_to_try = [
                'li.QjLAB7._75qWlu.iOzucJ',  # Original selector
                'li[data-testid*="product"]',  # Generic product selector
                'li[class*="product"]',  # Class containing product
                'li[class*="item"]',  # Class containing item
                'div[data-testid*="product"]',  # Div with product
                'article[data-testid*="product"]',  # Article with product
                'li',  # Fallback to any li
            ]
            
            items = None
            used_selector = None
            
            for selector in selectors_to_try:
                try:
                    tqdm.write(f"Trying selector: {selector}")
                    items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                    if len(items) > 0:
                        used_selector = selector
                        tqdm.write(f"✅ Found {len(items)} items with selector: {selector}")
                        break
                except Exception as e:
                    tqdm.write(f"Selector {selector} failed: {str(e)}")
                    continue
            
            if items is None or len(items) == 0:
                tqdm.write("No items found with any selector")
                return None
            
            if item_index >= len(items):
                tqdm.write(f"Item index {item_index} out of range (total: {len(items)})")
                return None
            
            item = items[item_index]
            
            # Try multiple selectors for product links
            link_selectors = [
                './/a[contains(@class, "CKDt_l")]',  # Original
                './/a[contains(@href, "/")]',  # Any link with href
                './/a',  # Any link
                './/a[contains(@data-testid, "product")]',  # Product link
            ]
            
            link = None
            for link_selector in link_selectors:
                try:
                    link = item.find_element(By.XPATH, link_selector)
                    tqdm.write(f"✅ Found link with selector: {link_selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if link is None:
                tqdm.write("Could not find product link")
                return None
                
            product_url = link.get_attribute('href')
            tqdm.write(f"Product URL: {product_url}")
            
            # Get product names with multiple selectors
            product_names = []
            name_selectors = [
                './/span[contains(@class, "ja2E95") and not(contains(@class, "voFjEy"))]',
                './/span[contains(@class, "voFjEy") and contains(@class, "ja2E95")]',
                './/h3',
                './/h2',
                './/span[contains(@class, "name")]',
                './/span[contains(@class, "title")]',
                './/div[contains(@class, "name")]',
                './/div[contains(@class, "title")]',
            ]
            
            for name_selector in name_selectors:
                try:
                    name_element = item.find_element(By.XPATH, name_selector)
                    name_text = name_element.text.strip()
                    if name_text:
                        product_names.append(name_text)
                        tqdm.write(f"✅ Found name with selector: {name_selector}")
                except NoSuchElementException:
                    continue
            
            product_name = " - ".join(product_names) if product_names else "Unknown Product"
            tqdm.write(f"Product name: {product_name}")
            
            # Get image URLs with multiple selectors
            img_selectors = [
                './/img[contains(@class, "_1RurXL")]',  # Original
                './/img[contains(@class, "image")]',
                './/img[contains(@class, "product")]',
                './/img[contains(@alt, "product")]',
                './/img',  # Any image
            ]
            
            main_img_url = None
            for img_selector in img_selectors:
                try:
                    img_element = item.find_element(By.XPATH, img_selector)
                    main_img_url = img_element.get_attribute('src')
                    if main_img_url:
                        tqdm.write(f"✅ Found main image with selector: {img_selector}")
                        break
                except NoSuchElementException:
                    continue
            
            if not main_img_url:
                tqdm.write("Could not find main image")
                return None
            
            # Try to get secondary image
            secondary_img_url = None
            try:
                secondary_img_element = item.find_element(By.XPATH, './/img[contains(@class, "OSvTKp")]')
                secondary_img_url = secondary_img_element.get_attribute('src')
                if secondary_img_url:
                    tqdm.write("✅ Found secondary image")
            except NoSuchElementException:
                tqdm.write("No secondary image found")
            
            # Get price with multiple selectors
            price_selectors = [
                './/section[contains(@class, "_0xLoFW")]//span[contains(@class, "voFjEy")]',
                './/span[contains(@class, "price")]',
                './/span[contains(@class, "cost")]',
                './/div[contains(@class, "price")]',
                './/span[contains(text(), "kr")]',
                './/span[contains(text(), "SEK")]',
            ]
            
            price = "Price not available"
            for price_selector in price_selectors:
                try:
                    price_element = item.find_element(By.XPATH, price_selector)
                    price_text = price_element.text.strip()
                    if price_text:
                        price = price_text
                        tqdm.write(f"✅ Found price with selector: {price_selector}")
                        break
                except NoSuchElementException:
                    continue
            
            return {
                'name': product_name,
                'url': product_url,
                'main_img_url': main_img_url,
                'secondary_img_url': secondary_img_url,
                'price': price
            }
            
        except (StaleElementReferenceException, TimeoutException) as e:
            tqdm.write(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
                continue
            else:
                tqdm.write(f"Failed to get product info after {max_retries} attempts")
                return None
        except Exception as e:
            tqdm.write(f"Unexpected error: {str(e)}")
            return None
    
    return None

def modify_image_url_to_packshot(img_url):
    """
    Try to modify a Zalando image URL to include packshot filter
    
    Args:
        img_url (str): Original image URL
    
    Returns:
        str: Modified URL with packshot filter, or original URL if modification not possible
    """
    if not img_url or 'img01.ztat.net' not in img_url:
        return img_url
    
    # If URL already has a filter parameter, replace it with packshot
    if 'filter=' in img_url:
        # Replace existing filter with packshot
        modified_url = img_url.replace('filter=', 'filter=packshot')
        tqdm.write(f"🔄 Modified existing filter to packshot: {modified_url}")
        return modified_url
    
    # If URL has imwidth parameter, add filter=packshot before it
    if 'imwidth=' in img_url:
        modified_url = img_url.replace('imwidth=', 'filter=packshot&imwidth=')
        tqdm.write(f"🔄 Added packshot filter: {modified_url}")
        return modified_url
    
    # If URL ends with .jpg, add filter parameter
    if img_url.endswith('.jpg'):
        modified_url = img_url + '?filter=packshot'
        tqdm.write(f"🔄 Added packshot filter to end: {modified_url}")
        return modified_url
    
    return img_url

def get_zalando_products_with_packshot_images(clothing_type, filters=None, max_items=5):
    """
    Get products from Zalando and automatically replace images with packshot images from product pages
    
    Args:
        clothing_type (str): Type of clothing from CLOTHING_TYPES mapping
        filters (dict): Dictionary of filters
        max_items (int): Maximum number of products to return
    
    Returns:
        list: List of product dictionaries with packshot images
    """
    # First, get products using the original function (from search results)
    tqdm.write(f"Getting products from search results...")
    products = get_zalando_products(clothing_type, filters, max_items)
    
    if not products:
        tqdm.write("No products found in search results")
        return []
    
    tqdm.write(f"Found {len(products)} products, getting packshot images...")
    
    # Initialize webdriver for visiting product pages
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Firefox(options=options)
    
    try:
        # Process each product
        packshot_products = []
        
        for i, product in enumerate(products, 1):
            tqdm.write(f"\nProcessing product {i}/{len(products)}: {product['name'][:50]}...")
            
            # Get packshot image from product page
            packshot_img_url = find_packshot_image(product['url'], driver)
            
            # Use packshot image if found, otherwise use the first available image
            if packshot_img_url:
                final_img_url = packshot_img_url
                packshot_found = True
            else:
                # Use the original image from search results
                final_img_url = product['image_url']
                packshot_found = False
            
            # Create product with packshot image
            packshot_product = {
                'name': product['name'],
                'url': product['url'],
                'image_url': final_img_url,
                'secondary_image_url': product.get('secondary_image_url'),
                'price': product['price'],
                'original_image': product['image_url'],
                'packshot_found': packshot_found
            }
            
            packshot_products.append(packshot_product)
            tqdm.write(f"✅ Processed product {i}")
        
        return packshot_products
        
    finally:
        driver.quit()

def extract_product_details_from_page(driver, product_url):
    """
    Extract detailed product information from a product page
    
    Args:
        driver: Selenium WebDriver instance
        product_url (str): URL of the product page
    
    Returns:
        dict: Dictionary containing detailed product information
    """
    try:
        # Navigate to product page
        tqdm.write(f"Navigating to: {product_url}")
        driver.get(product_url)
        time.sleep(3)  # Wait for content to load
        
        details = {
            'description': '',
            'material': None,
            'article_number': None,
            'manufacturing_info': None
        }
        
        # Extract material information from the material accordion
        try:
            tqdm.write("Extracting material information...")
            # Expand material accordion if needed
            try:
                material_accordion = driver.find_element(By.CSS_SELECTOR, '[data-testid="pdp-accordion-material_care"] button')
                aria_expanded = material_accordion.get_attribute('aria-expanded')
                if aria_expanded == 'false':
                    try:
                        material_accordion.click()
                        time.sleep(1)
                        tqdm.write("Material accordion expanded")
                    except Exception as e:
                        tqdm.write(f"Could not expand material accordion: {str(e)}")
            except Exception as e:
                tqdm.write(f"Material accordion button not found: {str(e)}")
            time.sleep(1)
            # Try to extract material from the accordion
            try:
                accordion_content = driver.find_element(By.CSS_SELECTOR, '[data-testid="pdp-accordion-material_care"]')
                # Try multiple selectors for term-definition pairs
                term_selectors = [
                    'dt.voFjEy.lystZ1.Sb5G3D.HlZ_Tf.zN9KaA',
                    'dt[role="term"]',
                    '.qMOFyE dt',
                    'dt'
                ]
                definition_selectors = [
                    'dd.voFjEy.lystZ1.m3OCL3.HlZ_Tf.zN9KaA',
                    'dd[role="definition"]',
                    '.qMOFyE dd',
                    'dd'
                ]
                terms = []
                definitions = []
                for term_selector, def_selector in zip(term_selectors, definition_selectors):
                    try:
                        terms = accordion_content.find_elements(By.CSS_SELECTOR, term_selector)
                        definitions = accordion_content.find_elements(By.CSS_SELECTOR, def_selector)
                        if terms and definitions:
                            break
                    except Exception as e:
                        continue
                if not terms or not definitions:
                    # Try direct dt/dd
                    terms = accordion_content.find_elements(By.CSS_SELECTOR, 'dt')
                    definitions = accordion_content.find_elements(By.CSS_SELECTOR, 'dd')
                for i, term in enumerate(terms):
                    if i < len(definitions):
                        try:
                            term_text = term.text.strip().replace(':', '')
                            if not term_text:
                                term_text = driver.execute_script("return arguments[0].textContent;", term).strip().replace(':', '')
                        except:
                            term_text = term.text.strip().replace(':', '')
                        try:
                            def_text = definitions[i].text.strip()
                            if not def_text:
                                def_text = driver.execute_script("return arguments[0].textContent;", definitions[i]).strip()
                        except:
                            def_text = definitions[i].text.strip()
                        if term_text.lower() == 'material' and def_text:
                            details['material'] = def_text
                            tqdm.write(f"Found material: {def_text}")
                            break
            except Exception as e:
                tqdm.write(f"Could not extract material from accordion: {str(e)}")
        except Exception as e:
            tqdm.write(f"Error extracting material: {str(e)}")

        # Extract detailed product information from the details accordion
        try:
            tqdm.write("Extracting specifications...")
            # Expand details accordion if needed
            try:
                details_accordion = driver.find_element(By.CSS_SELECTOR, '[data-testid="pdp-accordion-details"] button')
                aria_expanded = details_accordion.get_attribute('aria-expanded')
                if aria_expanded == 'false':
                    try:
                        details_accordion.click()
                        time.sleep(1)
                        tqdm.write("Details accordion expanded")
                    except Exception as e:
                        tqdm.write(f"Could not expand details accordion: {str(e)}")
            except Exception as e:
                tqdm.write(f"Details accordion button not found: {str(e)}")
            time.sleep(1)
            # Try to extract description from the accordion
            try:
                spec_container = driver.find_element(By.CSS_SELECTOR, '[data-testid="pdp-accordion-details"] div[style="white-space:pre-line"]')
                # Try multiple selectors for term-definition pairs
                term_selectors = [
                    'dt.voFjEy.lystZ1.Sb5G3D.HlZ_Tf.zN9KaA',
                    'dt[role="term"]',
                    '.qMOFyE dt',
                    'dt'
                ]
                definition_selectors = [
                    'dd.voFjEy.lystZ1.m3OCL3.HlZ_Tf.zN9KaA',
                    'dd[role="definition"]',
                    '.qMOFyE dd',
                    'dd'
                ]
                terms = []
                definitions = []
                for term_selector, def_selector in zip(term_selectors, definition_selectors):
                    try:
                        terms = spec_container.find_elements(By.CSS_SELECTOR, term_selector)
                        definitions = spec_container.find_elements(By.CSS_SELECTOR, def_selector)
                        if terms and definitions:
                            break
                    except Exception as e:
                        continue
                if not terms or not definitions:
                    # Try direct dt/dd
                    terms = spec_container.find_elements(By.CSS_SELECTOR, 'dt')
                    definitions = spec_container.find_elements(By.CSS_SELECTOR, 'dd')
                description_parts = []
                spec_mapping = {}
                for i, term in enumerate(terms):
                    if i < len(definitions):
                        try:
                            term_text = term.text.strip().replace(':', '')
                            if not term_text:
                                term_text = driver.execute_script("return arguments[0].textContent;", term).strip().replace(':', '')
                        except:
                            term_text = term.text.strip().replace(':', '')
                        try:
                            def_text = definitions[i].text.strip()
                            if not def_text:
                                def_text = driver.execute_script("return arguments[0].textContent;", definitions[i]).strip()
                        except:
                            def_text = definitions[i].text.strip()
                        spec_mapping[term_text] = def_text
                        description_parts.append(f"{term_text}: {def_text}")
                if 'Krage' in spec_mapping:
                    details['collar'] = spec_mapping['Krage']
                if 'Förslutning' in spec_mapping:
                    details['closure'] = spec_mapping['Förslutning']
                if 'Mönster' in spec_mapping:
                    details['pattern'] = spec_mapping['Mönster']
                if 'Detaljer' in spec_mapping:
                    details['details'] = spec_mapping['Detaljer']
                if 'Artikelnummer' in spec_mapping:
                    details['article_number'] = spec_mapping['Artikelnummer']
                if description_parts:
                    details['description'] = ' | '.join(description_parts)
                    tqdm.write(f"Combined description: {details['description']}")
            except Exception as e:
                tqdm.write(f"Could not extract description from details accordion: {str(e)}")
        except Exception as e:
            tqdm.write(f"Error extracting specifications: {str(e)}")

        # Try to extract manufacturing information
        try:
            tqdm.write("Looking for manufacturing info...")
            manufacturing_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-haspopup="dialog"] span.heWLCX.ZkIJC-.r9BRio.qXofat')
            if manufacturing_button:
                details['manufacturing_info'] = manufacturing_button.text.strip()
                tqdm.write(f"Found manufacturing info: {details['manufacturing_info']}")
        except Exception as e:
            tqdm.write(f"Error extracting manufacturing info: {str(e)}")
        
        tqdm.write(f"Final results - Material: {details['material']}, Description: {details['description'][:100]}...")
        return details
        
    except Exception as e:
        tqdm.write(f"Error extracting product details from {product_url}: {str(e)}")
        return details

def get_all_clothing_types_detailed_data(items_per_type=3):
    """
    Fetch detailed product information from all clothing types
    
    Args:
        items_per_type (int): Number of items to fetch per clothing type (default: 3)
    
    Returns:
        list: List of dictionaries containing detailed product information for all clothing types
    """
    all_products_data = []
    
    # Initialize webdriver
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Firefox(options=options)
    
    try:
        # Process each clothing type
        for clothing_type in CLOTHING_TYPES.keys():
            tqdm.write(f"\n{'='*60}")
            tqdm.write(f"Processing clothing type: {clothing_type}")
            tqdm.write(f"{'='*60}")
            
            try:
                # Get products for this clothing type
                products = get_zalando_products(clothing_type, max_items=items_per_type)
                
                if not products:
                    tqdm.write(f"No products found for {clothing_type}")
                    continue
                
                tqdm.write(f"Found {len(products)} products for {clothing_type}")
                
                # Process each product to get detailed information
                for i, product in enumerate(products, 1):
                    tqdm.write(f"\nProcessing product {i}/{len(products)}: {product['name'][:50]}...")
                    
                    # Extract detailed information from product page
                    detailed_info = extract_product_details_from_page(driver, product['url'])
                    
                    # Combine basic product info with detailed info
                    complete_product_info = {
                        'clothing_type': clothing_type,
                        'name': product['name'],
                        'url': product['url'],
                        'original_url': product['url'],  # Keep original URL
                        'image_url': product['image_url'],
                        'price': product['price'],
                        'material': detailed_info['material'],
                        'description': detailed_info['description'],
                        'article_number': detailed_info['article_number'],
                        'manufacturing_info': detailed_info['manufacturing_info']
                    }
                    
                    all_products_data.append(complete_product_info)
                    tqdm.write(f"✅ Completed product {i}")
                
            except Exception as e:
                tqdm.write(f"Error processing clothing type {clothing_type}: {str(e)}")
                continue
        
        return all_products_data
        
    finally:
        driver.quit()

def create_product_table(products_data):
    """
    Create a formatted table from product data
    
    Args:
        products_data (list): List of product dictionaries
    
    Returns:
        str: Formatted table string
    """
    if not products_data:
        return "No products data available"
    
    # Define table headers
    headers = [
        'Clothing Type', 'Name', 'Price', 'Material', 'Dominant Color', 
        'Dominant Tone', 'Dominant Hue', 'Dominant Shade', 'Color Count',
        'Description', 'Article Number', 'Original URL'
    ]
    
    # Create table header
    table = "| " + " | ".join(headers) + " |\n"
    table += "|" + "|".join(["---"] * len(headers)) + "|\n"
    
    # Add data rows
    for product in products_data:
        # Truncate description if too long
        description = product.get('description', '')
        if len(description) > 100:
            description = description[:97] + '...'
        
        row = [
            product.get('clothing_type', ''),
            product.get('name', '')[:50] + ('...' if len(product.get('name', '')) > 50 else ''),
            product.get('price', ''),
            product.get('material', ''),
            product.get('dominant_color_hex', ''),
            product.get('dominant_tone', ''),
            product.get('dominant_hue', ''),
            product.get('dominant_shade', ''),
            product.get('color_count', ''),
            description,
            product.get('article_number', ''),
            f"[Link]({product.get('original_url', '')})"
        ]
        table += "| " + " | ".join(str(cell) for cell in row) + " |\n"
    
    return table

def save_products_to_csv(products_data, filename='zalando_products_detailed.csv'):
    """
    Save product data to CSV file
    
    Args:
        products_data (list): List of product dictionaries
        filename (str): Output CSV filename
    """
    import csv
    
    if not products_data:
        tqdm.write("No data to save")
        return
    
    # Define fieldnames including color information and packshot data
    fieldnames = [
        'clothing_type', 'name', 'price', 'material', 'description', 
        'article_number', 'manufacturing_info', 'original_url', 'image_url',
        'original_image_url', 'packshot_found',
        # Color information
        'dominant_color_hex', 'dominant_color_rgb', 'dominant_tone', 
        'dominant_hue', 'dominant_shade', 'overall_tone', 'overall_hue', 
        'overall_shade', 'color_count', 'neutral_colors', 'color_extraction_success'
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in products_data:
                # Create a clean row with only the specified fields
                row = {field: product.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        tqdm.write(f"✅ Data saved to {filename}")
        
    except Exception as e:
        tqdm.write(f"Error saving to CSV: {str(e)}")

# Example usage:
if __name__ == "__main__":
    # Example with search query
    products = get_zalando_products('shirts', {
        'color': 'RED',
        'size': 'M',
        'material': 'linne',
        'q': 'randig'  # Search query
    }, max_items=5)

    # Print results
    for i, product in enumerate(products, 1):
        tqdm.write(f"Product {i}:")
        tqdm.write(f"Name: {product['name']}")
        tqdm.write(f"Price: {product['price']}")
        tqdm.write(f"URL: {product['url']}")
        tqdm.write(f"Main Image: {product['image_url']}")
        if product['secondary_image_url']:
            tqdm.write(f"Secondary Image: {product['secondary_image_url']}")
        tqdm.write("-" * 50)

    # Example of packshot image replacement
    tqdm.write("\n" + "="*60)
    tqdm.write("PACKSHOT IMAGE REPLACEMENT EXAMPLE")
    tqdm.write("="*60)
    
    # Get products with packshot images
    packshot_products = get_zalando_products_with_packshot_images('shirts', {
        'color': 'BLUE',
        'size': 'M'
    }, max_items=3)
    
    for i, product in enumerate(packshot_products, 1):
        tqdm.write(f"\nProduct {i}: {product['name'][:50]}...")
        tqdm.write(f"Price: {product['price']}")
        tqdm.write(f"Final Image: {product['image_url']}")
        
        # Show what was changed
        if product['original_image'] != product['image_url']:
            tqdm.write(f"🔄 Image was replaced with packshot:")
            tqdm.write(f"   Original: {product['original_image']}")
            tqdm.write(f"   Packshot: {product['image_url']}")
        else:
            tqdm.write(f"⚠️ No packshot found, using original image")
        
        tqdm.write(f"Packshot found: {product['packshot_found']}")
        tqdm.write("-" * 50)

    # Example of detailed data collection from all clothing types
    tqdm.write("\n" + "="*60)
    tqdm.write("DETAILED DATA COLLECTION FROM ALL CLOTHING TYPES")
    tqdm.write("="*60)
    
    # Uncomment the following lines to run the detailed data collection
    # This will take some time as it visits each product page
    """
    tqdm.write("Starting detailed data collection...")
    detailed_products = get_all_clothing_types_detailed_data(items_per_type=2)
    
    if detailed_products:
        tqdm.write(f"\nCollected data for {len(detailed_products)} products")
        
        # Create and display table
        table = create_product_table(detailed_products)
        tqdm.write("\n" + "="*80)
        tqdm.write("PRODUCT DETAILS TABLE")
        tqdm.write("="*80)
        tqdm.write(table)
        
        # Save to CSV
        save_products_to_csv(detailed_products, 'zalando_detailed_products.csv')
        
        # Show summary statistics
        tqdm.write(f"\n" + "="*40)
        tqdm.write("SUMMARY STATISTICS")
        tqdm.write("="*40)
        
        # Count by clothing type
        type_counts = {}
        for product in detailed_products:
            clothing_type = product['clothing_type']
            type_counts[clothing_type] = type_counts.get(clothing_type, 0) + 1
        
        for clothing_type, count in type_counts.items():
            tqdm.write(f"{clothing_type}: {count} products")
        
        # Count products with material information
        products_with_material = sum(1 for p in detailed_products if p.get('material'))
        tqdm.write(f"\nProducts with material info: {products_with_material}/{len(detailed_products)}")
        
        # Count products with article numbers
        products_with_article = sum(1 for p in detailed_products if p.get('article_number'))
        tqdm.write(f"Products with article numbers: {products_with_article}/{len(detailed_products)}")
    else:
        tqdm.write("No detailed product data collected")
    """
