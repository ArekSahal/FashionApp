#!/usr/bin/env python3
"""
Tag Coverage Report for FashionApp

- Connects to Supabase
- Fetches all products with their tags
- For each tag in ALLOWED_TAGS, counts how many products have that tag
- Prints a table of tag counts

Usage:
    python tag_coverage_report.py
"""
from supabase_db import SupabaseDB
from allowed_tags import ALLOWED_TAGS
from collections import Counter

try:
    from tabulate import tabulate
    USE_TABULATE = True
except ImportError:
    USE_TABULATE = False

def main():
    db = SupabaseDB()
    products = db.get_all_products_with_tags()
    tag_counter = Counter()
    total_products = len(products)
    for product in products:
        tags = product.get("Tags")
        if tags and isinstance(tags, list):
            tag_counter.update(tags)
    # Prepare table data
    table_data = []
    for tag in ALLOWED_TAGS:
        count = tag_counter.get(tag, 0)
        table_data.append([tag, count])
    # Print table
    print(f"\nTag Coverage Report (Total products: {total_products})\n")
    if USE_TABULATE:
        print(tabulate(table_data, headers=["Tag", "Product Count"], tablefmt="grid"))
    else:
        print(f"{'Tag':<25} | {'Product Count':>13}")
        print("-" * 41)
        for row in table_data:
            print(f"{row[0]:<25} | {row[1]:>13}")

if __name__ == "__main__":
    main() 