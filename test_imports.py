#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly.
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    # Test 1: Basic imports
    try:
        from config import Config
        print("✅ config.Config imported successfully")
    except Exception as e:
        print(f"❌ config.Config import failed: {e}")
        return False
    
    # Test 2: search_function imports
    try:
        import search_function
        print("✅ search_function imported successfully")
    except Exception as e:
        print(f"❌ search_function import failed: {e}")
        return False
    
    # Test 3: outfit_prompt_parser imports
    try:
        from outfit_prompt_parser import OutfitPromptParser
        print("✅ outfit_prompt_parser.OutfitPromptParser imported successfully")
    except Exception as e:
        print(f"❌ outfit_prompt_parser import failed: {e}")
        return False
    
    # Test 4: Flask app imports
    try:
        from app import app
        print("✅ app.app imported successfully")
    except Exception as e:
        print(f"❌ app.app import failed: {e}")
        return False
    
    print("✅ All imports successful!")
    return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("🎉 All imports are working correctly!")
    else:
        print("❌ Some imports failed!")
        sys.exit(1) 