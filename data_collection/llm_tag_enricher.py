#!/usr/bin/env python3
"""
LLM Tag Enricher for FashionApp

- Connects to Supabase
- Fetches all products
- For each product with empty/null Tags:
    - Gathers name, material, clothing_type, description, and image
    - Downloads and resizes the image
    - Sends info to an LLM to generate exhaustive fashion/style tags
    - Updates the Tags column in the database

Usage:
    python llm_tag_enricher.py
"""
import os
import io
import requests
from PIL import Image
from typing import List
from supabase_db import SupabaseDB
import logging
import openai
import base64
from allowed_tags import ALLOWED_TAGS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LLM model and API key (set your key in the environment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4.1-nano"  # Or your preferred model

# Resize image to this size before sending to LLM
IMAGE_SIZE = (256, 256)


def download_and_resize_image(image_url: str, size=(256, 256)) -> bytes:
    """Download image from URL and resize it, returning bytes."""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content)).convert("RGB")
        img = img.resize(size, Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.error(f"Error downloading/resizing image: {e}")
        return None


def generate_tags_with_llm(name: str, material: str, clothing_type: str, description: str, image_bytes: bytes, secondary_image_bytes: bytes = None):
    """
    Call the LLM to generate exhaustive fashion/style tags for the product.
    Returns a tuple: (list of tags, prompt_tokens, completion_tokens)
    """
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set.")
        return [], 0, 0
    try:
        # Prepare prompt
        allowed_tags_str = ", ".join(ALLOWED_TAGS)
        prompt = (
            "You are a fashion and style expert. "
            "Given the following product information and two images (if available), generate a comma-separated list of all relevant fashion and style tags that could help categorize or style this item in outfits. "
            "Only use tags from the following allowed list. Do not use any tags that are not in this list. "
            "Be as detailed and broad as possible, but only use the allowed tags. "
            "Do not repeat tags. Only output the tags, separated by commas.\n\n"
            f"Allowed tags: {allowed_tags_str}\n"
            f"Name: {name}\nMaterial: {material}\nClothing Type: {clothing_type}\nDescription: {description}\n"
        )
        # Encode images to base64
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        # Create OpenAI client
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        # Build content list for user message
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
        ]
        if secondary_image_bytes:
            secondary_image_b64 = base64.b64encode(secondary_image_bytes).decode("utf-8")
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{secondary_image_b64}"}})
        # Call OpenAI Vision model
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a fashion and style expert."},
                {"role": "user", "content": content},
            ],
            max_completion_tokens=2560,
        )
        tags_text = response.choices[0].message.content
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
        # Token usage
        usage = getattr(response, "usage", None)
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        return tags, prompt_tokens, completion_tokens
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        return [], 0, 0


def main():
    db = SupabaseDB()
    products = db.get_all_products(limit=1000)  # Adjust limit as needed
    logger.info(f"Fetched {len(products)} products from database.")
    updated_count = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    for product in products:
        tags = product.get("Tags")
        if tags and isinstance(tags, list) and len(tags) > 0:
            continue  # Already has tags
        # Gather fields
        name = product.get("name", "")
        material = product.get("material", "")
        clothing_type = product.get("clothing_type", "")
        description = product.get("description", "")
        image_url = product.get("image_url", "")
        secondary_image_url = product.get("original_image_url", "")
        original_url = product.get("original_url", "")
        if not (name and clothing_type and image_url and original_url):
            logger.warning(f"Skipping product with missing fields: {original_url}")
            continue
        # Download and resize images
        image_bytes = download_and_resize_image(image_url, IMAGE_SIZE)
        secondary_image_bytes = None
        if secondary_image_url:
            secondary_image_bytes = download_and_resize_image(secondary_image_url, IMAGE_SIZE)
        if not image_bytes:
            logger.warning(f"Skipping product due to image error: {original_url}")
            continue
        # Generate tags
        tags, prompt_tokens, completion_tokens = generate_tags_with_llm(
            name, material, clothing_type, description, image_bytes, secondary_image_bytes
        )
        total_prompt_tokens += prompt_tokens
        total_completion_tokens += completion_tokens
        if not tags:
            logger.warning(f"No tags generated for: {original_url}")
            continue
        # Update tags in DB
        success = db.update_tags(original_url, tags)
        if success:
            updated_count += 1
            logger.info(f"Updated tags for {original_url}: {tags}")
        else:
            logger.error(f"Failed to update tags for {original_url}")
    logger.info(f"Tag enrichment complete. Updated {updated_count} products.")
    # Print OpenAI API cost summary
    input_cost = (total_prompt_tokens / 1_000_000) * 0.1
    output_cost = (total_completion_tokens / 1_000_000) * 0.4
    total_cost = input_cost + output_cost
    print(f"\nOpenAI API usage summary:")
    print(f"  Total prompt tokens: {total_prompt_tokens}")
    print(f"  Total completion tokens: {total_completion_tokens}")
    print(f"  Estimated input cost: ${input_cost:.4f}")
    print(f"  Estimated output cost: ${output_cost:.4f}")
    print(f"  Total estimated cost: ${total_cost:.4f}\n")

if __name__ == "__main__":
    main() 