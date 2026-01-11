# Deploying UniDownload to Render

This guide will walk you through deploying UniDownload to Render.

## Prerequisites

- A GitHub account
- A Render account (free tier available at https://render.com)
- Your code pushed to GitHub

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure all files are committed and pushed to GitHub:
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Sign Up/Login to Render

1. Go to https://render.com
2. Sign up for free or log in
3. Click "Dashboard"

### 3. Create New Web Service

1. Click **"New +"** button
2. Select **"Web Service"**
3. Choose **"Build and deploy from a Git repository"**
4. Click **"Connect GitHub"** if not already connected
5. Find and select your **UniDownload** repository

### 4. Configure Web Service

Fill in the following settings:

**Basic Settings:**
- **Name**: `unidownload` (or your preferred name)
- **Region**: Choose closest to your location
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty
- **Runtime**: `Python 3`

**Build Settings:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn server:app`

**Instance Type:**
- Select **"Free"** tier (or upgrade if needed)

### 5. Environment Variables (Optional)

Add these if needed:
- `FLASK_ENV`: `production`
- `PORT`: Render sets this automatically

### 6. Deploy

1. Click **"Create Web Service"**
2. Render will start building your application
3. Wait for build to complete (2-5 minutes)
4. Once deployed, you'll get a URL like: `https://unidownload.onrender.com`

### 7. Access Your App

Click the URL provided by Render to access your deployed application!

## Post-Deployment

### Custom Domain (Optional)

1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain
4. Update DNS records as instructed

### Monitoring

- View logs in the Render dashboard
- Monitor app performance
- Check for errors in real-time

## Troubleshooting

### Build Fails

**Check:**
- `requirements.txt` has all dependencies
- Python version compatibility
- Build logs for specific errors

### App Crashes

**Common issues:**
- Missing environment variables
- Port configuration (Render sets PORT automatically)
- Check logs in Render dashboard

### Downloads Not Working

**Note:** Render free tier has limitations:
- Limited disk space (downloads stored temporarily)
- Service may sleep after inactivity
- Consider using persistent storage for production

## Important Notes

### Free Tier Limitations

- App sleeps after 15 minutes of inactivity
- 750 hours/month free
- Limited bandwidth
- No persistent storage

### Recommendations for Production

1. **Upgrade to Paid Plan** for:
   - No sleep time
   - More resources
   - Persistent storage
   - Better performance

2. **Add Persistent Storage**:
   - Use external storage (AWS S3, Cloudinary)
   - Database for tracking downloads
   - Cloud storage integration

3. **Enable Auto-Deploy**:
   - Render auto-deploys on push to main branch
   - Set up in service settings

## Alternative: Deploy with Docker

If you prefer Docker:

1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:5000"]
```

2. Deploy using Render's Docker support

## Support

If you encounter issues:
1. Check Render logs
2. Review [Render documentation](https://render.com/docs)
3. Open an issue on GitHub

## Success!

Your UniDownload app should now be live and accessible worldwide! 🎉

Share your deployment URL and start downloading media from anywhere!
