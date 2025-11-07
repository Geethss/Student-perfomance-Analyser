# Deployment Guide for Render

This guide explains how to deploy the Student Performance Analyzer application on Render.

## Prerequisites

1. A [Render](https://render.com) account (free tier is sufficient)
2. A GitHub account with this repository
3. A Google Gemini API key

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure all the following files are in your repository:
- `app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration
- `.streamlit/config.toml` - Streamlit configuration
- Supporting modules: `gemini_analyzer.py`, `document_processor.py`, `report_generator.py`

### 2. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 3. Create New Web Service on Render

1. Log in to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** button
3. Select **"Web Service"**

### 4. Connect Your Repository

1. Choose **"Build and deploy from a Git repository"**
2. Click **"Connect account"** if not already connected to GitHub
3. Select your repository from the list
4. Click **"Connect"**

### 5. Configure the Service

Render will automatically detect `render.yaml` and use those settings. Verify:

- **Name**: `student-performance-analyzer`
- **Region**: Choose closest to your users (default: Oregon)
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
- **Plan**: Free (or paid plan for better performance)

### 6. Set Environment Variables

**Important**: Add your Google Gemini API key:

1. In the Render dashboard, go to your service
2. Navigate to **"Environment"** tab
3. Add environment variable:
   - **Key**: `GOOGLE_API_KEY`
   - **Value**: Your actual Google Gemini API key
4. Click **"Save Changes"**

### 7. Deploy

1. Click **"Create Web Service"** or **"Deploy"**
2. Wait for the build to complete (5-10 minutes for first deployment)
3. Once deployed, you'll receive a URL like: `https://student-performance-analyzer.onrender.com`

## Post-Deployment

### Accessing Your Application

Your app will be available at the URL provided by Render. Share this URL with users.

### Monitoring

- View logs in real-time from the Render dashboard
- Check deployment history
- Monitor resource usage (CPU, memory)

### Updating the Application

To update your deployed application:

1. Make changes to your code locally
2. Commit and push to GitHub:
```bash
git add .
git commit -m "Update description"
git push origin main
```
3. Render will automatically detect changes and redeploy

### Free Tier Limitations

The Render free tier includes:
- ✓ 750 hours per month
- ✓ Auto-sleep after 15 minutes of inactivity
- ✓ Cold start time (~30 seconds when waking up)
- ⚠️ Service spins down with inactivity
- ⚠️ Limited to 512 MB RAM

**Tip**: Upgrade to a paid plan for:
- No auto-sleep
- More resources
- Better performance
- Custom domains

## Troubleshooting

### Build Failures

If the build fails:
1. Check the build logs in Render dashboard
2. Verify all dependencies are in `requirements.txt`
3. Ensure Python version compatibility

### Application Not Starting

If app doesn't start:
1. Check the deploy logs
2. Verify the start command is correct
3. Ensure environment variables are set

### API Key Issues

If you get API errors:
1. Verify `GOOGLE_API_KEY` is set in environment variables
2. Check the API key is valid and active
3. Ensure you have API quota remaining

### PDF Processing Errors

If PDF processing fails, you may need to add system dependencies. Create a file named `packages.txt`:

```
poppler-utils
```

This installs poppler which is required for `pdf2image`.

## Alternative: Manual Configuration

If you prefer not to use `render.yaml`:

1. Choose **"Web Service"** manually
2. Configure:
   - **Name**: Your choice
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
3. Set environment variables as described above

## Security Notes

- Never commit `.env` files with actual API keys
- Always use environment variables for sensitive data
- Rotate API keys periodically
- Monitor API usage to prevent abuse

## Support

For issues specific to:
- **Render deployment**: Check [Render Documentation](https://render.com/docs)
- **Streamlit**: See [Streamlit Docs](https://docs.streamlit.io/)
- **Gemini API**: Visit [Google AI Documentation](https://ai.google.dev/docs)

## Cost Optimization

For optimal performance while managing costs:

1. **Free Tier**: Good for testing and low traffic
2. **Starter Plan ($7/month)**: 
   - No auto-sleep
   - Better for regular use
   - Faster response times
3. **Standard Plan**: For production use with high traffic

Choose based on your usage patterns and requirements.

