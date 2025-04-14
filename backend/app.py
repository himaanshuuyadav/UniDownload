from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os
import time

app = Flask(__name__, static_folder="../frontend", static_url_path="/")

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

# CORS
if app.debug:
    CORS(app)
else:
    CORS(app, resources={r"/*": {"origins": [
        "https://unidownload.onrender.com",
    ]}})

# Use /tmp for safe download path on Render
DOWNLOAD_FOLDER = "/tmp"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_youtube_qualities(url):
    """Fetch best unique MP4 qualities for a YouTube video."""
    try:
        ydl_opts = {
            "quiet": False,
            "verbose": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=False)
            except yt_dlp.utils.DownloadError as e:
                print("DownloadError during info fetch:", e)
                if "Video unavailable" in str(e):
                    return {"error": "This video is unavailable. It might be private, deleted, or region-restricted."}
                return {"error": str(e)}

            formats = info_dict.get("formats", [])

        video_info = {
            "title": info_dict.get("title", "Unknown"),
            "thumbnail": info_dict.get("thumbnail", ""),
        }

        best_qualities = {}
        for fmt in formats:
            if fmt.get("vcodec") != "none" and fmt.get("acodec") == "none" and fmt.get("ext") == "mp4":
                resolution = f"{fmt.get('height', 'Unknown')}p"
                if resolution not in best_qualities or fmt.get("tbr", 0) > best_qualities[resolution]["tbr"]:
                    best_qualities[resolution] = {
                        "format_id": fmt["format_id"],
                        "resolution": resolution,
                        "ext": fmt["ext"],
                        "tbr": fmt.get("tbr", 0),
                    }

        qualities = sorted(best_qualities.values(), key=lambda x: int(x["resolution"].replace("p", "")), reverse=True)
        return {"qualities": qualities, "video_info": video_info}

    except Exception as e:
        print("Error fetching qualities:", e)
        return {"error": f"Error: {str(e)}"}

@app.route("/get_qualities", methods=["POST"])
def get_qualities():
    data = request.get_json()
    video_url = data.get("url")
    print("Fetching qualities for:", video_url)

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    if "youtube.com" in video_url or "youtu.be" in video_url:
        result = get_youtube_qualities(video_url)
        return jsonify(result)

    return jsonify({"error": "Unsupported URL"}), 400

@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    video_url = data.get("url")
    format_id = data.get("format_id")

    print("Download requested")
    print("URL:", video_url)
    print("Format ID:", format_id)

    if not video_url or not format_id:
        return jsonify({"error": "Invalid request"}), 400

    try:
        timestamp = int(time.time())
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'%(title)s_{timestamp}.%(ext)s'),
            'format': f"{format_id}+bestaudio[ext=m4a]",
            'merge_output_format': 'mp4',
            'quiet': False,
            'verbose': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            },
            'concurrent_fragment_downloads': 1,
            'retries': 10,
            'fragment_retries': 10,
            'file_access_retries': 10
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([video_url])
            except yt_dlp.utils.DownloadError as e:
                print("DownloadError during download:", e)
                if "Video unavailable" in str(e):
                    return jsonify({"error": "This video is unavailable. It might be private, deleted, or region-restricted."}), 400
                return jsonify({"error": str(e)}), 400

        return jsonify({"success": "Download completed successfully!"})

    except Exception as e:
        print("Unhandled error during download:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=10000)
