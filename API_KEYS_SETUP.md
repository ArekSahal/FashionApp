# API Keys Setup Guide

This guide explains how to securely manage your API keys for the Fashion App.

## 🔒 Security First

Your API keys are sensitive information that should never be committed to Git. This setup ensures your keys are kept secure.

## 🚀 Quick Setup

### Option 1: Interactive Setup (Recommended)

Run the setup script to configure your API keys interactively:

```bash
python setup_keys.py
```

This will:
- Guide you through entering your API keys
- Create a `.env` file automatically
- Validate your configuration
- Show you how to get your API keys

### Option 2: Manual Setup

1. **Create a `.env` file** in the project root:
   ```bash
   cp env.example .env
   ```

2. **Edit the `.env` file** and add your actual API keys:
   ```env
   # OpenAI API Key
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   
   # Supabase Configuration
   SUPABASE_KEY=your-actual-supabase-key-here
   SUPABASE_URL=https://your-project-id.supabase.co
   ```

3. **Validate your setup**:
   ```bash
   python config.py
   ```

## 🔑 Getting Your API Keys

### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### Supabase Keys

1. Go to [Supabase](https://supabase.com)
2. Sign in or create an account
3. Create a new project or select existing
4. Go to **Settings** > **API**
5. Copy the **anon public** key
6. Copy the **Project URL**

## 📁 File Structure

```
FashionApp/
├── .env                    # Your API keys (NOT tracked by Git)
├── .env.example           # Example format (tracked by Git)
├── config.py              # Configuration loader
├── setup_keys.py          # Interactive setup script
├── keys.py                # Backward compatibility
└── .gitignore             # Excludes .env from Git
```

## 🔧 How It Works

### Configuration Loading Priority

The system loads API keys in this order:

1. **Environment variables** (highest priority)
2. **`.env` file** (if exists)
3. **Default values** (lowest priority)

### Usage in Code

```python
from config import Config

# Access your API keys
openai_key = Config.OPENAI_API_KEY
supabase_key = Config.SUPABASE_KEY
supabase_url = Config.SUPABASE_URL

# Validate configuration
missing_keys = Config.validate_required_keys()
if missing_keys:
    print(f"Missing keys: {missing_keys}")

# Show configuration status
Config.print_status()
```

### Backward Compatibility

The old `keys.py` file still works but now uses the new config system:

```python
import keys

# Still works as before
api_key = keys.API_KEY
```

## 🛡️ Security Features

### Git Protection

- `.env` file is automatically excluded from Git
- API keys are never committed to version control
- Example files show format without real keys

### Key Validation

- Automatic validation of required keys
- Masked display of keys (shows only first/last few characters)
- Clear error messages for missing keys

### Environment Variables

You can also set keys as environment variables:

```bash
# Set environment variables
export OPENAI_API_KEY="sk-your-key-here"
export SUPABASE_KEY="your-supabase-key-here"
export SUPABASE_URL="https://your-project.supabase.co"

# Run your application
python ai_server/app.py
```

## 🔍 Troubleshooting

### "Missing API keys" Error

If you see missing API keys errors:

1. **Check your `.env` file**:
   ```bash
   cat .env
   ```

2. **Validate configuration**:
   ```bash
   python config.py
   ```

3. **Run setup again**:
   ```bash
   python setup_keys.py
   ```

### Import Errors

If you get import errors:

1. **Install dependencies**:
   ```bash
   pip install python-dotenv
   ```

2. **Check file structure**:
   ```bash
   ls -la .env config.py
   ```

### Permission Errors

If you can't create the `.env` file:

1. **Check permissions**:
   ```bash
   ls -la .env
   ```

2. **Create manually**:
   ```bash
   touch .env
   chmod 600 .env
   ```

## 📋 Configuration Status

Check your current configuration:

```bash
python config.py
```

This will show:
- ✅ Which keys are configured
- ❌ Which keys are missing
- 🔍 Masked preview of your keys
- 💡 Instructions for fixing issues

## 🔄 Adding New API Keys

To add new API keys:

1. **Add to `config.py`**:
   ```python
   NEW_API_KEY = os.getenv('NEW_API_KEY', '')
   ```

2. **Add to `.env` file**:
   ```env
   NEW_API_KEY=your-new-key-here
   ```

3. **Add to `env.example`**:
   ```env
   NEW_API_KEY=your_new_api_key_here
   ```

4. **Update validation** (if required):
   ```python
   required_keys = [
       'OPENAI_API_KEY',
       'SUPABASE_KEY',
       'NEW_API_KEY'  # Add here if required
   ]
   ```

## 🚨 Security Best Practices

1. **Never commit `.env` files** to Git
2. **Rotate your API keys** regularly
3. **Use environment variables** in production
4. **Keep your keys private** and secure
5. **Monitor API usage** to detect unauthorized access
6. **Use different keys** for development and production

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run `python setup_keys.py` for interactive help
3. Validate your configuration with `python config.py`
4. Check the `.gitignore` file to ensure `.env` is excluded

---

**Remember**: Your API keys are like passwords - keep them secure and never share them publicly! 