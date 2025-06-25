#!/usr/bin/env python3
"""
Enhanced FashionApp AI Server Runner for Railway

This script starts the Flask server with enhanced debugging and environment variable validation.
"""

import os
import sys
from dotenv import load_dotenv

def validate_environment():
    """Validate that all required environment variables are set."""
    print("🔍 VALIDATING ENVIRONMENT VARIABLES")
    print("=" * 50)
    
    # Load .env file if it exists
    load_dotenv()
    
    # Required environment variables
    required_vars = [
        'OPENAI_API_KEY',
        'SUPABASE_KEY',
        'SUPABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        else:
            # Mask sensitive values for logging
            if 'KEY' in var:
                masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n⚠️  WARNING: Missing required environment variables: {', '.join(missing_vars)}")
        print("💡 Make sure these are set in Railway dashboard under Variables tab")
        print("   The app may not function correctly without these variables.")
        return False
    
    print("\n✅ All required environment variables are set!")
    return True

def debug_railway_environment():
    """Debug Railway-specific environment variables."""
    print("\n🚂 RAILWAY ENVIRONMENT DEBUG")
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
    
    # Check if we're running on Railway
    if os.getenv('RAILWAY_PROJECT_ID'):
        print("✅ Running on Railway platform")
    else:
        print("⚠️  Not running on Railway platform (local development)")

def main():
    """Start the Flask server with enhanced validation"""
    try:
        print("🚀 STARTING FASHIONAPP AI SERVER")
        print("=" * 50)
        
        # Debug Railway environment
        debug_railway_environment()
        
        # Validate environment variables
        env_valid = validate_environment()
        
        # Import and test config
        print("\n⚙️ TESTING CONFIGURATION")
        print("-" * 30)
        try:
            from config import Config
            print("✅ Config module imported successfully")
            
            # Test config validation
            missing_keys = Config.validate_required_keys()
            if missing_keys:
                print(f"❌ Config validation failed: Missing {', '.join(missing_keys)}")
            else:
                print("✅ Config validation passed")
                
        except Exception as e:
            print(f"❌ Config import failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Import Flask app
        print("\n🌐 IMPORTING FLASK APP")
        print("-" * 30)
        try:
            from app import app
            print("✅ Flask app imported successfully")
            
            # Check parser initialization
            from app import parser
            if parser:
                print("✅ OutfitPromptParser initialized successfully")
            else:
                print("⚠️  OutfitPromptParser not initialized (limited mode)")
                
        except Exception as e:
            print(f"❌ Flask app import failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Get port from environment variable (Railway provides this)
        port = int(os.environ.get('PORT', 5003))
        print(f"\n🌐 STARTING SERVER ON PORT {port}")
        print("=" * 50)
        
        # Start the server
        app.run(
            host='0.0.0.0',  # Bind to all interfaces
            port=port,
            debug=False,     # Disable debug mode for production
            threaded=True    # Enable threading for better performance
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 