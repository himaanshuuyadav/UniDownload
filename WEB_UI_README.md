# UniDownload Web UI

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install flask flask-cors yt-dlp requests
   ```

2. **Start the server:**
   ```bash
   python server.py
   ```

3. **Open in browser:**
   Navigate to http://localhost:5000

## Features

- 🎬 **YouTube**: Multiple quality options, audio, subtitles, thumbnails, playlist support
- 📸 **Instagram**: Posts, reels, stories, audio extraction
- 📱 **Facebook**: Posts, videos, images, audio extraction
- 🔍 **Auto-detection**: Paste any URL and it detects the platform
- 📥 **Easy downloads**: Click any button to start downloading

## API Endpoints

### POST /api/detect
Detect platform and fetch media information
```json
{
  "url": "https://youtube.com/watch?v=..."
}
```

### POST /api/download
Download media with options
```json
{
  "url": "https://youtube.com/watch?v=...",
  "platform": "youtube",
  "option": "video",
  "format_id": "1080"
}
```

### GET /api/health
Health check endpoint

## Download Location

All downloads are saved to the `downloads/` folder in the project directory.

## Notes

- Instagram/Facebook posts requiring login need browser cookie authentication
- YouTube HD quality downloads require FFmpeg to be installed
- The server runs in debug mode by default (suitable for development only)

## Troubleshooting

**CSS/JS not loading?**
- Make sure files are in `static/` folder
- Check browser console for errors

**Downloads not working?**
- Verify the platform's downloader is properly configured
- Check terminal for error messages
- Ensure you have write permissions to the downloads folder

**Instagram/Facebook errors?**
- Try disabling cookies for public content
- Use Firefox instead of Chrome/Brave for cookie authentication
- Make sure content is publicly accessible
