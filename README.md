# UniDownload

🚀 Universal social media downloader with modern web interface

Download videos, images, and audio from YouTube, Instagram, and Facebook with a single click! Features a beautiful gradient UI with automatic platform detection.

## ✨ Features

### 🌐 Web Interface
- **Single Input Box** - Paste any social media URL
- **Auto-Detection** - Automatically detects YouTube, Instagram, or Facebook
- **Modern UI** - Beautiful gradient design with dark theme
- **Real-time Progress** - Track your downloads live
- **Mobile Responsive** - Works on all devices

### 📺 YouTube Support
- Video downloads (144p to 2160p 4K)
- Audio-only extraction (MP3)
- Subtitle/caption downloads
- Thumbnail downloads
- Playlist support
- Quality selection with format info

### 📸 Instagram Support
- Posts (photos and videos)
- Reels and IGTV
- Stories (with authentication)
- Carousel posts
- Audio extraction
- Cookie authentication support

### 📘 Facebook Support
- Video downloads
- Post content
- Quality selection
- Audio extraction
- Cookie authentication support

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/himaanshuuyadav/UniDownload.git
cd UniDownload
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install FFmpeg** (required for audio/video processing)
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **Linux**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`

4. **Run the server**
```bash
python server.py
```

5. **Open in browser**
```
http://localhost:5000
```

## 📦 Deployment on Render

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

### Quick Deploy Steps:
1. Fork/clone this repository to your GitHub
2. Create new Web Service on [Render](https://render.com)
3. Connect your GitHub repository
4. Render will auto-detect Python and use `Procfile`
5. Add environment variable: `FLASK_ENV=production`
6. Deploy!

## 🛠️ Tech Stack

- **Backend**: Flask 3.0.0 with RESTful API
- **Downloader**: yt-dlp (latest)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Server**: Gunicorn (production)
- **Media Processing**: FFmpeg

## 📡 API Endpoints

### POST `/api/detect`
Analyze a URL and get media information
```json
{
  "url": "https://youtube.com/watch?v=..."
}
```

**Response:**
```json
{
  "platform": "youtube",
  "title": "Video Title",
  "uploader": "Channel Name",
  "duration": 180,
  "thumbnail": "https://...",
  "formats": [...],
  "options": [...]
}
```

### POST `/api/download`
Download media with specified options
```json
{
  "url": "https://youtube.com/watch?v=...",
  "platform": "youtube",
  "option": "video",
  "format_id": "720"
}
```

### GET `/api/health`
Health check endpoint
```json
{
  "status": "ok"
}
```

## 📁 Project Structure

```
UniDownload/
├── server.py              # Flask API server
├── youtube.py             # YouTube downloader
├── instagram.py           # Instagram downloader
├── facebook.py            # Facebook downloader
├── static/
│   ├── index.html        # Web interface
│   ├── style.css         # Gradient UI design
│   └── script.js         # Frontend logic
├── downloads/            # Downloaded files
├── requirements.txt      # Python dependencies
├── Procfile             # Render deployment config
├── DEPLOYMENT.md        # Deployment guide
└── README.md            # This file
```

## 🔒 Authentication

For private Instagram/Facebook content, cookie authentication is supported:

1. Export cookies from your browser (use Firefox for best compatibility)
2. Save as `cookies.txt` in the project root
3. The downloaders will automatically use cookies when available

**Note**: Chrome/Brave cookies may have DPAPI encryption issues on Windows. Use Firefox for reliable cookie support.

## 🐛 Troubleshooting

### FFmpeg not found
- Ensure FFmpeg is installed and added to your system PATH
- Restart terminal/command prompt after installation
- Test with: `ffmpeg -version`

### Instagram showing "0 items"
- This usually means the content is private
- Export cookies from Firefox and save as `cookies.txt`
- Place the file in the project root directory

### API returns 500 error
- Check server logs for detailed error messages
- Ensure all dependencies are installed
- Verify FFmpeg is accessible

### Downloads not working on Render
- Check the deployment logs in Render dashboard
- Ensure FFmpeg buildpack is added (see DEPLOYMENT.md)
- Verify environment variables are set correctly

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes!

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## ⭐ Show Your Support

If you find this project helpful, please give it a star on GitHub!

## 📧 Contact

For issues and questions, please use the GitHub Issues page.

---

**Made with ❤️ using Flask, yt-dlp, and modern web technologies**
