# Railway Environment Variables Troubleshooting Guide

This guide helps you resolve issues with environment variables not being picked up by your FashionApp on Railway.

## Quick Diagnosis

### 1. Run the Debug Script

First, run the debug script to see what's happening:

```bash
# Locally (to test your setup)
python debug_env.py

# On Railway (check the logs)
# The enhanced server will automatically run diagnostics
```

### 2. Check Railway Dashboard

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Variables" tab
4. Verify these variables are set:
   - `OPENAI_API_KEY`
   - `SUPABASE_KEY`
   - `SUPABASE_URL`

## Common Issues and Solutions

### Issue 1: Environment Variables Not Loading

**Symptoms:**
- App starts but API calls fail
- "Missing required API keys" errors
- Parser not initializing

**Solutions:**

#### A. Check Variable Names
Make sure variable names are exactly correct (case-sensitive):
```bash
# ✅ Correct
OPENAI_API_KEY=sk-...
SUPABASE_KEY=eyJ...
SUPABASE_URL=https://...

# ❌ Wrong
openai_api_key=sk-...
SUPABASE_KEY=eyJ...
supabase_url=https://...
```

#### B. Check Variable Values
- No extra spaces or quotes
- No trailing whitespace
- Valid API keys

#### C. Redeploy After Changes
Railway requires a redeploy to pick up new environment variables:
1. Make changes in Variables tab
2. Go to Deployments tab
3. Click "Deploy" or wait for auto-deploy

### Issue 2: App Not Starting

**Symptoms:**
- Build fails
- App crashes on startup
- Health check fails

**Solutions:**

#### A. Check Railway Logs
1. Go to Railway dashboard
2. Click on your service
3. Go to "Logs" tab
4. Look for error messages

#### B. Use Enhanced Server
The enhanced server (`run_server_enhanced.py`) provides better debugging:
```bash
# Update Procfile to use enhanced server
web: python run_server_enhanced.py
```

#### C. Check Dependencies
Ensure all dependencies are in `requirements.txt`:
```
flask>=2.3.0
flask-cors>=4.0.0
python-dotenv>=1.0.0
openai>=1.0.0
supabase>=2.0.0
```

### Issue 3: Variables Loaded But App Still Fails

**Symptoms:**
- Environment variables are present
- Config loads successfully
- But API calls still fail

**Solutions:**

#### A. Check API Key Validity
Test your API keys locally:
```python
import openai
from supabase import create_client

# Test OpenAI
client = openai.OpenAI(api_key="your-key")
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("✅ OpenAI key works")
except Exception as e:
    print(f"❌ OpenAI key failed: {e}")

# Test Supabase
supabase = create_client("your-url", "your-key")
try:
    response = supabase.table("test").select("*").limit(1).execute()
    print("✅ Supabase key works")
except Exception as e:
    print(f"❌ Supabase key failed: {e}")
```

#### B. Check Network Access
Railway might have network restrictions. Test basic connectivity:
```python
import requests

try:
    response = requests.get("https://api.openai.com/v1/models", 
                          headers={"Authorization": f"Bearer {api_key}"})
    print(f"✅ OpenAI API accessible: {response.status_code}")
except Exception as e:
    print(f"❌ OpenAI API not accessible: {e}")
```

## Step-by-Step Debugging Process

### Step 1: Verify Local Setup
```bash
# Test locally with .env file
cp env.example .env
# Edit .env with your keys
python debug_env.py
```

### Step 2: Check Railway Variables
1. Go to Railway dashboard
2. Variables tab
3. Verify all required variables are set
4. Check for typos or extra characters

### Step 3: Test with Enhanced Server
```bash
# Update Procfile
web: python run_server_enhanced.py

# Deploy and check logs
```

### Step 4: Check Railway Logs
Look for these messages in Railway logs:
- ✅ "All required environment variables are set!"
- ✅ "Config validation passed"
- ✅ "OutfitPromptParser initialized successfully"

### Step 5: Test Health Endpoint
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "parser_ready": true,
  "database_connected": true,
  "server_mode": "full"
}
```

## Environment Variable Reference

### Required Variables
```bash
# OpenAI API Key (for AI functionality)
OPENAI_API_KEY=sk-...

# Supabase Configuration (for database)
SUPABASE_KEY=eyJ...
SUPABASE_URL=https://your-project.supabase.co
```

### Optional Variables
```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false

# Port (Railway sets this automatically)
PORT=5003

# Python Path
PYTHONPATH=.
```

## Railway-Specific Considerations

### 1. Variable Persistence
- Variables persist across deployments
- Changes require redeploy to take effect
- Variables are encrypted at rest

### 2. Build vs Runtime
- Variables are available at runtime, not build time
- Use `os.getenv()` not hardcoded values
- Test with `debug_env.py` script

### 3. Service Dependencies
If using multiple services:
- Variables are service-specific
- Use Railway's variable sharing if needed
- Check service connections

## Testing Your Fix

### 1. Local Test
```bash
# Set environment variables locally
export OPENAI_API_KEY="your-key"
export SUPABASE_KEY="your-key"
export SUPABASE_URL="your-url"

# Test the app
python run_server_enhanced.py
```

### 2. Railway Test
```bash
# Deploy to Railway
git add .
git commit -m "Fix environment variables"
git push

# Check logs for success messages
# Test health endpoint
curl https://your-app.railway.app/health
```

### 3. Full Functionality Test
```bash
# Test the main endpoint
curl -X POST https://your-app.railway.app/search_outfit \
  -H "Content-Type: application/json" \
  -d '{"prompt": "summer casual outfit"}'
```

## Common Error Messages and Solutions

### "Missing required API keys"
- Check variable names in Railway dashboard
- Ensure no extra spaces or quotes
- Redeploy after changes

### "Config module imported successfully" but "Config validation failed"
- Variables are loading but values are empty
- Check API key format and validity
- Verify no trailing whitespace

### "OutfitPromptParser not initialized"
- Usually means OpenAI API key is invalid
- Test API key locally first
- Check network connectivity

### "Database connection failed"
- Supabase credentials issue
- Check URL format and key validity
- Verify database permissions

## Getting Help

If you're still having issues:

1. **Check Railway Documentation**: https://docs.railway.app
2. **Review Logs**: Railway dashboard → Logs tab
3. **Test Locally**: Use `debug_env.py` script
4. **Verify API Keys**: Test keys independently
5. **Check Network**: Ensure Railway can reach external APIs

## Prevention Tips

1. **Use Enhanced Server**: Always use `run_server_enhanced.py` for better debugging
2. **Test Locally First**: Always test with `.env` file before deploying
3. **Validate Keys**: Test API keys independently before using
4. **Monitor Logs**: Check Railway logs regularly
5. **Use Debug Script**: Run `debug_env.py` when troubleshooting 