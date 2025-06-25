#!/usr/bin/env python3
"""
API Keys Setup Script

This script helps set up API keys securely for the FashionApp.
"""

import os
from pathlib import Path

def create_env_file():
    """Create a .env file with API keys"""
    env_file = Path('.env')
    
    if env_file.exists():
        return False
    
    # Get user input for API keys
    openai_key = input("OpenAI API Key: ").strip()
    supabase_key = input("Supabase Key: ").strip()
    supabase_url = input("Supabase URL: ").strip()
    
    # Create .env file content
    env_content = f"""# FashionApp API Keys
# This file contains your API keys and should NOT be committed to Git

OPENAI_API_KEY={openai_key}
SUPABASE_KEY={supabase_key}
SUPABASE_URL={supabase_url}
"""
    
    # Write to .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        return True
    except Exception as e:
        return False

def validate_configuration():
    """Validate the current configuration"""
    try:
        from config import Config
        config = Config()
        
        # Check for missing keys
        missing_keys = []
        if not config.openai_api_key:
            missing_keys.append('OPENAI_API_KEY')
        if not config.supabase_key:
            missing_keys.append('SUPABASE_KEY')
        if not config.supabase_url:
            missing_keys.append('SUPABASE_URL')
        
        return len(missing_keys) == 0, missing_keys
        
    except ImportError:
        return False, ['config module']

def show_help():
    """Show help information for getting API keys"""
    help_text = """
HOW TO GET YOUR API KEYS:
==================================================

🔑 OpenAI API Key:
   1. Go to https://platform.openai.com/api-keys
   2. Sign in or create an account
   3. Click 'Create new secret key'
   4. Copy the key (starts with 'sk-')

🔑 Supabase Keys:
   1. Go to https://supabase.com
   2. Sign in or create an account
   3. Create a new project or select existing
   4. Go to Settings > API
   5. Copy the 'anon public' key
   6. Copy the project URL

🔒 Security Notes:
   - Never commit your .env file to Git
   - Keep your API keys secure and private
   - Rotate your keys regularly
   - Use environment variables in production
"""
    return help_text

def main():
    """Main function with menu interface"""
    while True:
        try:
            choice = input("Choose an option:\n1. Set up API keys (create .env file)\n2. Validate current configuration\n3. Show help (how to get API keys)\n4. Exit\nEnter choice (1-4): ")
            
            if choice == "1":
                if create_env_file():
                    # Validate the new configuration
                    is_valid, missing_keys = validate_configuration()
                    if is_valid:
                        pass
                    else:
                        pass
                else:
                    pass
                    
            elif choice == "2":
                is_valid, missing_keys = validate_configuration()
                if is_valid:
                    pass
                else:
                    pass
                    
            elif choice == "3":
                help_text = show_help()
                pass
                
            elif choice == "4":
                break
                
            else:
                pass
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            pass

if __name__ == "__main__":
    main() 