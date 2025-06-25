# Railway Deployment Guide for FashionApp

This guide will help you deploy your FashionApp on Railway using the provided configuration files.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your FashionApp should be in a GitHub repository
3. **Environment Variables**: You'll need to set up your API keys and database credentials

## Project Structure

The FashionApp has been reorganized for better deployment:

```
FashionApp/
├── app.py                    # Main Flask application
├── run_server.py            # Server startup script
├── search_function.py       # Database search functionality
├── outfit_prompt_parser.py  # AI prompt parsing
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── tests/                  # All test files
├── docs/                   # Documentation files
├── logs/                   # Application logs
├── data_collection/        # Data collection scripts
├── nixpacks.toml          # Railway build configuration
├── Procfile               # Alternative deployment method
├── start.sh               # Startup script
└── railway.toml           # Railway configuration
```

## Configuration Files Created

The following files have been created for Railway deployment:

- `railway.toml` - Main Railway configuration
- `nixpacks.toml` - Nixpacks build configuration (newer standard)
- `Procfile` - Alternative deployment method
- `start.sh` - Startup script
- `.railwayignore` - Files to exclude from deployment
- `runtime.txt` - Python version specification
- Updated `run_server.py` - Now uses PORT environment variable
- Updated `requirements.txt` - Added missing Flask dependency

## Deployment Steps

### 1. Connect Your Repository

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your FashionApp repository
5. Railway will automatically detect it's a Python project

### 2. Set Environment Variables

In your Railway project dashboard, go to the "Variables" tab and add the following environment variables:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Optional: Database credentials (if using separate database)
DATABASE_URL=your_database_url_here

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false
```

### 3. Deploy

1. Railway will automatically detect the configuration files
2. The build process will install dependencies from `requirements.txt`
3. The server will start using the command specified in `nixpacks.toml`
4. Railway will run health checks on the `/health` endpoint

### 4. Access Your App

Once deployed, Railway will provide you with:
- A public URL (e.g., `https://your-app-name.railway.app`)
- Custom domain options (if you have one)

## API Endpoints

Your deployed app will have the following endpoints:

- `GET /health` - Health check endpoint
- `POST /search_outfit` - Main outfit search endpoint
- `POST /parse_prompt` - Parse outfit prompts only
- `POST /search_outfit_dummy` - Dummy search for testing

## Example Usage

```bash
# Health check
curl https://your-app-name.railway.app/health

# Search for an outfit
curl -X POST https://your-app-name.railway.app/search_outfit \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "old money summer vibe with deep autumn colors",
    "top_results_per_item": 3,
    "sort_by_price": true,
    "price_order": "asc"
  }'
```

## Troubleshooting

### Common Issues

1. **Build Fails**: Check that all dependencies are in `requirements.txt`
2. **App Won't Start**: Verify environment variables are set correctly
3. **Health Check Fails**: Ensure the `/health` endpoint is working
4. **Database Connection Issues**: Verify Supabase credentials

### Nixpacks Build Issues

If you encounter "No start command could be found" error:

1. **Check Configuration Files**: Ensure all configuration files are committed to your repository
2. **Multiple Start Methods**: The deployment uses multiple fallback methods:
   - `nixpacks.toml` (primary)
   - `Procfile` (fallback)
   - `start.sh` script (alternative)
3. **Dependencies**: Make sure `requirements.txt` includes Flask:
   ```
   flask>=2.3.0
   flask-cors>=4.0.0
   ```
4. **File Permissions**: The `start.sh` script is made executable during build

### Logs

- View logs in the Railway dashboard under the "Deployments" tab
- Check the "Logs" tab for real-time application logs

### Environment Variables

Make sure these are set in Railway:
- `OPENAI_API_KEY` - Required for AI functionality
- `SUPABASE_URL` - Required for database access
- `SUPABASE_KEY` - Required for database access

## Local Development

For local development, you can still use:

```bash
# Run the main app
python run_fashionapp.py

# Or run the AI server directly
python run_server.py
```

## Monitoring

Railway provides:
- Automatic health checks
- Restart on failure
- Real-time logs
- Performance metrics
- Custom domains

## Cost Optimization

- Railway offers a free tier with limitations
- Monitor your usage in the Railway dashboard
- Consider upgrading if you need more resources

## Security Notes

- Never commit API keys to your repository
- Use Railway's environment variables for sensitive data
- The app runs with CORS enabled for all origins (modify if needed)
- Consider adding authentication for production use

## Support

If you encounter issues:
1. Check Railway's documentation
2. Review the logs in Railway dashboard
3. Verify all environment variables are set
4. Test locally first to isolate issues
5. Check that all configuration files are properly committed 