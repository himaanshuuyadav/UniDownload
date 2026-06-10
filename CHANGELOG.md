# Changelog

## v1.0.0 (2026-06-10)

Initial release.

### Features

- **Instagram post downloading** — download single-image posts via yt-dlp
- **Instagram carousel downloading** — detect and download all images in a carousel (supports any number of slides)
- **Instagram reel downloading** — download reel videos with format selection (highest resolution + bitrate)
- **Single-image fallback** — yt-dlp's Instagram extractor normally crashes on image-only posts; the backend patches this gap with GraphQL/API extraction
- **Chrome Extension UI** — popup with Analyze, Download Current, Download All buttons
- **Flask backend** — REST API at `127.0.0.1:5000` with three endpoints (`/analyze`, `/download-current`, `/download-all`)
- **yt-dlp integration** — all media extraction and downloading goes through yt-dlp; no DOM scraping, no browser automation
- **Debug panel** — collapsible popup panel showing backend status, yt-dlp status, extracted URL list
- **Safe format selection** — handles null width, height, bitrate, fps, filesize without crashing

### Technical notes

- Three monkey patches applied to yt-dlp's Instagram extractor to fix image-only gaps
- No `scripting` or `downloads` Chrome permissions required
- Backend uses `detect_platform()` for future extensibility (YouTube, TikTok, etc.)
