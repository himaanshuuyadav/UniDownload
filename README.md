# UniDownload

> Universal media downloader powered by yt-dlp

Download media from supported websites through a Chrome Extension + Python Flask backend. No DOM scraping, no browser automation — all extraction is handled by yt-dlp.

## Features

- **Instagram posts** — single images
- **Instagram carousels** — any number of slides
- **Instagram reels** — video download with format selection
- **Extensible architecture** — add YouTube, TikTok, X/Twitter with minimal code
- **Local backend** — everything runs on your machine at `127.0.0.1:5000`
- **Private by design** — no accounts, no cloud, no tracking

## Architecture

```
┌──────────────────────┐     HTTP POST /analyze     ┌─────────────────────┐
│  Chrome Extension    │  ───────────────────────►   │  Flask Backend      │
│  (Manifest V3)        │  ◄───────────────────────   │  (server.py)        │
│                      │     JSON response           │                     │
│  extension/           │                             │  POST /analyze      │
│    manifest.json      │                             │  POST /download-*   │
│    popup/             │                             └────────┬────────────┘
│    background/        │                                      │
│    icons/             │                                      ▼
└──────────────────────┘                              ┌─────────────────────┐
                                                     │  yt-dlp             │
                                                     │  (extraction API)    │
                                                     └─────────────────────┘
```

## Quick start

### Prerequisites

- Python 3.8+
- Chrome or Edge (Chromium-based)
- pip

### 1. Install the extension

1. Open `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select the `extension/` folder

### 2. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start the backend

```bash
cd backend
python server.py
```

Expected output:
```
UniDownload Backend starting on http://127.0.0.1:5000
  Media:  .../backend/downloads/media
  Videos: .../backend/downloads/videos
```

### 4. Use the extension

1. Navigate to an Instagram post (`/p/...`) or reel (`/reel/...`)
2. Click the UniDownload extension icon
3. Click **Analyze**
4. Review the detected content type and media count
5. Click **Download Current** or **Download All**

## Project structure

```
UniDownload/
├── extension/                    # Chrome Extension (MV3)
│   ├── manifest.json             # Extension manifest
│   ├── popup/
│   │   ├── popup.html            # Popup UI
│   │   ├── popup.css             # Popup styles
│   │   └── popup.js              # Popup controller
│   ├── background/
│   │   └── background.js         # Service worker
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
├── backend/                      # Python Flask backend
│   ├── server.py                 # Flask app + yt-dlp extraction
│   └── requirements.txt          # Python dependencies
├── README.md
├── LICENSE                       # MIT
├── CHANGELOG.md
└── .gitignore
```

## API reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/analyze` | POST | Extract media metadata from a URL |
| `/download-current` | POST | Download a single media item |
| `/download-all` | POST | Download every item in a carousel |
| `/health` | GET | Backend health check |

All requests and responses use JSON.

### `POST /analyze`

```json
// Request
{ "url": "https://www.instagram.com/p/ABC123/" }

// Response (success)
{
  "success": true,
  "post_type": "carousel",
  "media_count": 5,
  "items": [
    { "index": 1, "url": "...cdn...", "type": "image", "ext": "jpg" },
    { "index": 2, "url": "...cdn...", "type": "image", "ext": "jpg" }
  ],
  "title": "Post caption",
  "uploader": "username",
  "shortcode": "ABC123",
  "ytdl_status": "ok"
}
```

### `POST /download-current`

```json
// Request
{ "url": "...", "post_type": "carousel", "index": 1 }

// Response
{ "success": true, "files": [".../downloads/media/instagram_20240101_120000_1.jpg"], "count": 1 }
```

### `POST /download-all`

```json
// Request
{ "url": "...", "post_type": "carousel" }

// Response
{ "success": true, "files": ["...1.jpg", "...2.jpg", "..."], "count": 5 }
```

## File naming

Downloaded files are saved under `backend/downloads/`:

| Content type | Directory | Pattern |
|---|---|---|
| Single image | `media/` | `{platform}_YYYYMMDD_HHMMSS_1.jpg` |
| Carousel | `media/` | `{platform}_YYYYMMDD_HHMMSS_1.jpg`, `_2.jpg`, ... |
| Video / reel | `videos/` | `{platform}_reel_YYYYMMDD_HHMMSS.mp4` |

The `{platform}` prefix identifies the source (e.g. `instagram`).

## Debugging

Open the collapsible **Debug Info** panel in the extension popup:

- Backend connection status
- yt-dlp extraction status
- Extracted URL count
- Raw URLs for each item

The backend also saves the complete yt-dlp response to `backend/debug/debug.json`
on every analyze request (add `debug/` yourself or remove the save call in production).

## Roadmap

- [ ] **YouTube** — video and audio extraction
- [ ] **TikTok** — video downloads without watermark
- [ ] **X/Twitter** — image and video extraction
- [ ] **Facebook** — public video downloads
- [ ] **Download history** — track previously saved files
- [ ] **Batch URL support** — analyze multiple URLs at once
- [ ] **Custom output directory** — user-configurable save location

## Permissions

| Permission | Reason |
|---|---|
| `activeTab` | Read the current tab's URL |
| `http://127.0.0.1:5000/*` | Communicate with the local Python backend |

No `scripting`, no `downloads`, no `host_permissions` beyond localhost.

## Known limitations

- yt-dlp cannot download private/authenticated posts without cookies.
  Pass cookies via `--cookies-from-browser chrome` in backend flags.
- The backend must be running before clicking **Analyze**.
- Currently supports Instagram only; other platforms require adding URL patterns
  to `detect_platform()` and `classify_url()`.

## License

MIT — see [LICENSE](LICENSE).
