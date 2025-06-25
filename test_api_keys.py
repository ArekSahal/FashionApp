#!/usr/bin/env python3
"""
API Key Validation Script

This script tests the validity of your OpenAI and Supabase API keys.
Run this locally to verify your keys work before deploying to Railway.
"""

import os
import sys
from dotenv import load_dotenv

def test_openai_key(api_key):
    """Test OpenAI API key validity."""
    try:
        import openai
        
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello World'"}],
            max_tokens=10
        )
        
        print("✅ OpenAI API key is valid")
        print(f"   Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API key failed: {e}")
        return False

def test_supabase_connection(url, key):
    """Test Supabase connection."""
    try:
        from supabase import create_client, Client
        
        supabase: Client = create_client(url, key)
        
        # Test basic connection (this will fail if credentials are wrong)
        # We'll try to get the schema info
        response = supabase.table("clothing_types").select("*").limit(1).execute()
        
        print("✅ Supabase connection successful")
        print(f"   URL: {url}")
        print(f"   Tables accessible: Yes")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def main():
    """Main validation function."""
    print("🔑 API KEY VALIDATION")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase_url = os.getenv('SUPABASE_URL')
    
    if not openai_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("   Set it with: export OPENAI_API_KEY='your-key'")
        print("   Or add it to your .env file")
        return False
    
    if not supabase_key:
        print("❌ SUPABASE_KEY not found in environment")
        print("   Set it with: export SUPABASE_KEY='your-key'")
        print("   Or add it to your .env file")
        return False
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in environment")
        print("   Set it with: export SUPABASE_URL='your-url'")
        print("   Or add it to your .env file")
        return False
    
    print("📋 Testing API Keys...")
    print("-" * 30)
    
    # Test OpenAI
    print("\n🤖 Testing OpenAI API...")
    openai_valid = test_openai_key(openai_key)
    
    # Test Supabase
    print("\n🗄️ Testing Supabase connection...")
    supabase_valid = test_supabase_connection(supabase_url, supabase_key)
    
    # Summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 30)
    
    if openai_valid and supabase_valid:
        print("✅ All API keys are valid!")
        print("   Your app should work correctly on Railway")
        return True
    else:
        print("❌ Some API keys failed validation")
        print("   Please fix the issues above before deploying")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 