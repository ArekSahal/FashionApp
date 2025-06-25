#!/usr/bin/env python3
"""
Data Collection Runner

This script provides a menu to run different data collection operations.
"""

from bulk_product_collector import collect_all_products_batch_upload
from detailed_product_collector import collect_detailed_products_individual

def main():
    """Main function with menu interface"""
    while True:
        try:
            choice = input("Choose an operation:\n1. Bulk Collection (100 items per type)\n2. Detailed Collection (individual processing)\n3. Exit\nEnter choice (1-3): ")
            
            if choice == "1":
                collect_all_products_batch_upload(items_per_type=100, batch_size=20)
            elif choice == "2":
                clothing_types = ['shirts', 't_shirts', 'shorts']
                collect_detailed_products_individual(clothing_types, items_per_type=3, use_database=True)
            elif choice == "3":
                break
            else:
                pass
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            pass

if __name__ == "__main__":
    main() 