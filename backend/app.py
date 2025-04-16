import os
import json
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

# Create a directory for cookies
COOKIE_DIR = "/tmp/cookies"
os.makedirs(COOKIE_DIR, exist_ok=True)
COOKIE_FILE = os.path.join(COOKIE_DIR, "youtube.cookies")

# Safe download folder for Render
DOWNLOAD_FOLDER = "/tmp"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Add this function to initialize a cookie file
def init_cookie_file():
    # Create a basic cookie structure if file doesn't exist
    if not os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, 'w') as f:
            cookies = [
                {
                    "name": "CONSENT",
                    "value": "YES+cb",
                    "domain": ".youtube.com",
                    "path": "/",
                    "secure": True
                }
            ]
            json.dump(cookies, f)

# Call this at the start of your application
init_cookie_file()

# List of proxies to rotate
PROXIES = [
    'http://103.231.218.30:80',       # Bangladesh
    'http://51.77.73.150:3128',       # France
    'http://103.105.49.53:80',        # Vietnam
    'http://45.167.125.61:9992',      # Brazil
]

# Proxy-aware yt-dlp config
# Updated proxy handling
def get_ydl_opts(format_id=None):
    opts = {
        'outtmpl': os.path.join("/tmp", '%(title)s_%(id)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': False,
        'verbose': True,
        'cookiefile': COOKIE_FILE,  # Use cookies to avoid bot detection
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.youtube.com/',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android'],
                'player_skip': ['configs', 'webpage']
            }
        },
        'retries': 5,
        'fragment_retries': 5,
        'file_access_retries': 5,
        'socket_timeout': 30,
        'concurrent_fragment_downloads': 1
    }

    if format_id:
        opts['format'] = f"{format_id}+bestaudio[ext=m4a]"
    
    return opts

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

# Fetch qualities
@app.route("/get_qualities", methods=["POST"])
def get_qualities():
    data = request.get_json()
    video_url = data.get("url")
    
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400
    
    print("Starting get_qualities() call for URL:", video_url)
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            if not info:
                return jsonify({"error": "Could not extract video information"}), 400
                
            formats = info.get("formats", [])
            video_info = {
                "title": info.get("title", "Unknown"),
                "thumbnail": info.get("thumbnail", ""),
            }
            
            # Filter for MP4 video formats
            best_qualities = {}
            for fmt in formats:
                if fmt.get("vcodec") != "none" and fmt.get("acodec") == "none" and fmt.get("ext") == "mp4":
                    resolution = f"{fmt.get('height', 'Unknown')}p"
                    if resolution not in best_qualities or fmt.get("tbr", 0) > best_qualities[resolution]["tbr"]:
                        best_qualities[resolution] = {
                            "format_id": fmt["format_id"],
                            "resolution": resolution,
                            "ext": fmt["ext"],
                            "tbr": fmt.get("tbr", 0)
                        }
            
            qualities = sorted(best_qualities.values(), key=lambda x: int(x["resolution"].replace("p", "")), reverse=True)
            
            if not qualities:
                return jsonify({"error": "No downloadable formats found for this video"}), 400
                
            return jsonify({"qualities": qualities, "video_info": video_info})
    except yt_dlp.utils.DownloadError as e:
        print("yt-dlp error during info fetch:", e)
        error_msg = str(e)
        if "Sign in to confirm you're not a bot" in error_msg:
            return jsonify({"error": "YouTube detected automation. Try again later or with a different video."}), 400
        elif "private" in error_msg.lower():
            return jsonify({"error": "This video is private or unavailable."}), 400
        else:
            return jsonify({"error": "Unable to fetch video information. YouTube may be restricting access."}), 400
    except Exception as e:
        print("General error during get_qualities:", e)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Handle downloads
@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    video_url = data.get("url")
    format_id = data.get("format_id")

    if not video_url or not format_id:
        return jsonify({"error": "Invalid request"}), 400

    try:
        with yt_dlp.YoutubeDL(get_ydl_opts(format_id)) as ydl:
            ydl.download([video_url])
        return jsonify({"success": "Download completed successfully!"})
    except yt_dlp.utils.DownloadError as e:
        print("yt-dlp error during download:", e)
        return jsonify({"error": "Download failed. Video may be private, deleted, or restricted."}), 400
    except Exception as e:
        print("General error during download:", e)
        return jsonify({"error": str(e)}), 500

# Run the server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
