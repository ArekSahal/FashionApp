#!/usr/bin/env python3
"""
Main entry point for FashionApp.
Provides easy access to both data collection and AI server operations.
"""

import sys
import os

def main():
    print("👗 FashionApp - AI-Powered Outfit Search")
    print("=" * 50)
    print("Choose an operation:")
    print("1. Data Collection (Scrape products from Zalando)")
    print("2. Start AI Server (Run the outfit search API)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                print("\n🔄 Starting data collection...")
                os.chdir("data_collection")
                os.system("python run_collection.py")
                break
                
            elif choice == "2":
                print("\n🤖 Starting AI server...")
                os.system("python run_server.py")
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