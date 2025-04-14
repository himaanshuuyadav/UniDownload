from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
if app.debug:
    CORS(app)
else:
    CORS(app, resources={r"/*": {"origins": [
        "https://your-frontend.netlify.app",  # Replace with your actual frontend URL
    ]}})

DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def get_youtube_qualities(url):
    """Fetch best unique MP4 qualities for a YouTube video."""
    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get("formats", [])

        # Get video metadata
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
        return {"error": str(e)}


@app.route("/get_qualities", methods=["POST"])
def get_qualities():
    """Get video qualities for a given URL."""
    data = request.get_json()
    video_url = data.get("url")

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    if "youtube.com" in video_url or "youtu.be" in video_url:
        result = get_youtube_qualities(video_url)
        return jsonify(result)  # Return the complete result object

    return jsonify({"error": "Unsupported URL"}), 400


@app.route("/download", methods=["POST"])
def download_video():
    """Download the selected video format with audio."""
    data = request.get_json()
    video_url = data.get("url")
    format_id = data.get("format_id")

    if not video_url or not format_id:
        return jsonify({"error": "Invalid request"}), 400

    try:
        # Use a unique filename based on timestamp
        import time
        timestamp = int(time.time())
        
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'%(title)s_{timestamp}.%(ext)s'),
            'format': f"{format_id}+bestaudio[ext=m4a]",
            'merge_output_format': 'mp4',
            'quiet': False,
            'no_warnings': False,
            'concurrent_fragment_downloads': 1,  # Disable concurrent downloads
            'retries': 10,  # Increase retry attempts
            'fragment_retries': 10,
            'file_access_retries': 10
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        return jsonify({"success": "Download completed successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)