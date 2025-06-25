#!/usr/bin/env python3
"""
Setup script for API keys configuration.
This script helps you set up your API keys securely.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """
    Create a .env file with API keys from user input.
    """
    print("🔑 API Keys Setup")
    print("=" * 50)
    print("This script will help you set up your API keys securely.")
    print("Your keys will be stored in a .env file that is NOT tracked by Git.")
    print()
    
    # Check if .env already exists
    env_file = Path('.env')
    if env_file.exists():
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite not in ['y', 'yes']:
            print("Setup cancelled.")
            return
    
    # Get API keys from user
    print("\n📝 Please enter your API keys:")
    print("(Press Enter to skip if you don't have a key yet)")
    
    openai_key = input("\n🔑 OpenAI API Key: ").strip()
    supabase_key = input("🔑 Supabase Anon Key: ").strip()
    supabase_url = input("🌐 Supabase URL (optional, press Enter for default): ").strip()
    
    # Use default Supabase URL if not provided
    if not supabase_url:
        supabase_url = "https://ohgyxtkvyffvycfpvxcq.supabase.co"
    
    # Create .env file content
    env_content = f"""# API Keys Configuration
# This file contains your API keys and is NOT tracked by Git

# OpenAI API Key
OPENAI_API_KEY={openai_key}

# Supabase Configuration
SUPABASE_KEY={supabase_key}
SUPABASE_URL={supabase_url}

# Optional: Other API keys you might need
# GOOGLE_API_KEY=your_google_api_key_here
# STRIPE_SECRET_KEY=your_stripe_secret_key_here
# AWS_ACCESS_KEY_ID=your_aws_access_key_here
# AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
"""
    
    # Write to .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ .env file created successfully!")
        print(f"📁 Location: {env_file.absolute()}")
        
        # Show what was configured
        print(f"\n📋 Configuration Summary:")
        if openai_key:
            print(f"   ✅ OpenAI API Key: {openai_key[:8]}...{openai_key[-4:]}")
        else:
            print(f"   ❌ OpenAI API Key: Not set")
            
        if supabase_key:
            print(f"   ✅ Supabase Key: {supabase_key[:8]}...{supabase_key[-4:]}")
        else:
            print(f"   ❌ Supabase Key: Not set")
            
        print(f"   ✅ Supabase URL: {supabase_url}")
        
        # Validate configuration
        print(f"\n🔍 Validating configuration...")
        validate_configuration()
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False
    
    return True

def validate_configuration():
    """
    Validate the current configuration.
    """
    try:
        from config import Config
        
        missing_keys = Config.validate_required_keys()
        
        if missing_keys:
            print(f"⚠️  Missing required keys: {', '.join(missing_keys)}")
            print("   Please add them to your .env file or set them as environment variables")
        else:
            print("✅ All required API keys are configured!")
            
    except ImportError:
        print("⚠️  Could not import config module")
        print("   Make sure you have the required dependencies installed")

def show_help():
    """
    Show help information for getting API keys.
    """
    print("\n💡 How to get your API keys:")
    print("=" * 50)
    
    print("\n🔑 OpenAI API Key:")
    print("   1. Go to https://platform.openai.com/api-keys")
    print("   2. Sign in or create an account")
    print("   3. Click 'Create new secret key'")
    print("   4. Copy the key (starts with 'sk-')")
    
    print("\n🔑 Supabase Keys:")
    print("   1. Go to https://supabase.com")
    print("   2. Sign in or create an account")
    print("   3. Create a new project or select existing")
    print("   4. Go to Settings > API")
    print("   5. Copy the 'anon public' key")
    print("   6. Copy the project URL")
    
    print("\n🔒 Security Notes:")
    print("   - Never commit your .env file to Git")
    print("   - Keep your API keys secure and private")
    print("   - Rotate your keys regularly")
    print("   - Use environment variables in production")

def main():
    """
    Main setup function.
    """
    print("🚀 Fashion App API Keys Setup")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Set up API keys (create .env file)")
        print("2. Validate current configuration")
        print("3. Show help (how to get API keys)")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            create_env_file()
        elif choice == '2':
            validate_configuration()
        elif choice == '3':
            show_help()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main() 