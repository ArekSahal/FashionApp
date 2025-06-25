#!/usr/bin/env python3
"""
Debug script to troubleshoot Railway environment variable issues.
This script will help identify if environment variables are being loaded correctly.
"""

import os
from dotenv import load_dotenv

def debug_environment():
    """Debug environment variables and configuration loading."""
    
    print("🔍 ENVIRONMENT VARIABLE DEBUG")
    print("=" * 50)
    
    # Load .env file if it exists
    print("📁 Loading .env file...")
    load_dotenv()
    
    # Print all environment variables (be careful with sensitive data)
    print("\n🌍 ALL ENVIRONMENT VARIABLES:")
    print("-" * 30)
    for key, value in sorted(os.environ.items()):
        # Mask sensitive values
        if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'password', 'token']):
            masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"{key}: {masked_value}")
        else:
            print(f"{key}: {value}")
    
    # Test specific Railway environment variables
    print("\n🚂 RAILWAY-SPECIFIC VARIABLES:")
    print("-" * 30)
    railway_vars = [
        'PORT',
        'RAILWAY_STATIC_URL',
        'RAILWAY_PUBLIC_DOMAIN',
        'RAILWAY_PROJECT_ID',
        'RAILWAY_SERVICE_ID'
    ]
    
    for var in railway_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    # Test our specific API keys
    print("\n🔑 API KEY VARIABLES:")
    print("-" * 30)
    api_keys = [
        'OPENAI_API_KEY',
        'SUPABASE_KEY',
        'SUPABASE_URL'
    ]
    
    for key in api_keys:
        value = os.getenv(key)
        if value:
            masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"✅ {key}: {masked_value}")
        else:
            print(f"❌ {key}: Not set")
    
    # Test config loading
    print("\n⚙️ CONFIG LOADING TEST:")
    print("-" * 30)
    try:
        from config import Config
        print("✅ Config module imported successfully")
        
        # Test config values
        openai_key = Config.OPENAI_API_KEY
        supabase_key = Config.SUPABASE_KEY
        supabase_url = Config.SUPABASE_URL
        
        if openai_key:
            masked_openai = f"{openai_key[:8]}...{openai_key[-4:]}" if len(openai_key) > 12 else "***"
            print(f"✅ OPENAI_API_KEY loaded: {masked_openai}")
        else:
            print("❌ OPENAI_API_KEY not loaded")
            
        if supabase_key:
            masked_supabase = f"{supabase_key[:8]}...{supabase_key[-4:]}" if len(supabase_key) > 12 else "***"
            print(f"✅ SUPABASE_KEY loaded: {masked_supabase}")
        else:
            print("❌ SUPABASE_KEY not loaded")
            
        if supabase_url:
            print(f"✅ SUPABASE_URL loaded: {supabase_url}")
        else:
            print("❌ SUPABASE_URL not loaded")
            
        # Validate required keys
        missing = Config.validate_required_keys()
        if missing:
            print(f"❌ Missing required keys: {', '.join(missing)}")
        else:
            print("✅ All required keys are present")
            
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Flask app initialization
    print("\n🌐 FLASK APP TEST:")
    print("-" * 30)
    try:
        from app import app
        print("✅ Flask app imported successfully")
        
        # Check if parser was initialized
        from app import parser
        if parser:
            print("✅ OutfitPromptParser initialized successfully")
        else:
            print("❌ OutfitPromptParser not initialized")
            
    except Exception as e:
        print(f"❌ Error importing Flask app: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_environment() 