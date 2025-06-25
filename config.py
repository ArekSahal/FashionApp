#!/usr/bin/env python3
"""
Configuration file for API keys and sensitive data.
This file loads API keys from environment variables or a .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """
    Configuration class that loads API keys and other sensitive data.
    Prioritizes environment variables, then .env file, then defaults.
    """
    
    # OpenAI API Key
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Supabase Configuration
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://ohgyxtkvyffvycfpvxcq.supabase.co')
    
    # Add other API keys as needed
    # GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    # STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    # AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    # AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    
    @classmethod
    def validate_required_keys(cls):
        """
        Validate that required API keys are present.
        
        Returns:
            list: List of missing required keys
        """
        required_keys = [
            'OPENAI_API_KEY',
            'SUPABASE_KEY'
        ]
        
        missing_keys = []
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
        
        return missing_keys
    
    @classmethod
    def print_status(cls):
        """
        Print the status of all API keys (without revealing the actual keys).
        """
        print("🔑 API Key Status:")
        print("=" * 50)
        
        # Check required keys
        missing_keys = cls.validate_required_keys()
        
        if missing_keys:
            print("❌ Missing required API keys:")
            for key in missing_keys:
                print(f"   - {key}")
            print("\n💡 To fix this:")
            print("   1. Create a .env file in the project root")
            print("   2. Add your API keys to the .env file")
            print("   3. Or set them as environment variables")
        else:
            print("✅ All required API keys are configured")
        
        # Show status of all keys
        all_keys = [
            'OPENAI_API_KEY',
            'SUPABASE_KEY', 
            'SUPABASE_URL'
        ]
        
        print(f"\n📋 Key Configuration Status:")
        for key in all_keys:
            value = getattr(cls, key)
            if value:
                # Show first 8 characters and last 4 characters for security
                masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                print(f"   ✅ {key}: {masked_value}")
            else:
                print(f"   ❌ {key}: Not set")

# Create a convenient alias for backward compatibility
API_KEY = Config.OPENAI_API_KEY

# Example usage and validation
if __name__ == "__main__":
    Config.print_status()
    
    missing = Config.validate_required_keys()
    if missing:
        print(f"\n⚠️  Missing required keys: {', '.join(missing)}")
        print("Please set these environment variables or add them to .env file")
    else:
        print(f"\n✅ Configuration is ready!") 