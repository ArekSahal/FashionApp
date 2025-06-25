# Railway Deployment Guide for FashionApp

This guide will help you deploy your FashionApp on Railway using the provided configuration files.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your FashionApp should be in a GitHub repository
3. **Environment Variables**: You'll need to set up your API keys and database credentials

## Configuration Files Created

The following files have been created for Railway deployment:

- `railway.toml` - Main Railway configuration
- `Procfile` - Alternative deployment method
- `.railwayignore` - Files to exclude from deployment
- `runtime.txt` - Python version specification
- Updated `ai_server/run_server.py` - Now uses PORT environment variable

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
3. The server will start using the command specified in `railway.toml`
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
cd ai_server
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