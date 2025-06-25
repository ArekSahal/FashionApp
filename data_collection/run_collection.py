#!/usr/bin/env python3
"""
Entry point for data collection operations.
Provides easy access to different collection scripts.
"""

import sys
import os

def main():
    print("🚀 FashionApp Data Collection")
    print("=" * 40)
    print("Choose an operation:")
    print("1. Bulk Collection (100 items per type)")
    print("2. Detailed Collection (individual processing)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                print("\n🔄 Starting bulk collection...")
                from bulk_product_collector import main as bulk_main
                bulk_main()
                break
                
            elif choice == "2":
                print("\n🔄 Starting detailed collection...")
                from detailed_product_collector import main as detailed_main
                detailed_main()
                break
                
            elif choice == "3":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n👋 Operation cancelled.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    main() 