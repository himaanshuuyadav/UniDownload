# backend/youtube_downloader.py
import requests
import re

PIPED_API_BASE = "https://pipedapi.kavin.rocks"


def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", url)
    return match.group(1) if match else None


def is_valid_youtube_url(url):
    return bool(extract_video_id(url))


def get_video_qualities_api(url):
    if not is_valid_youtube_url(url):
        return {"error": "Invalid YouTube URL"}

    video_id = extract_video_id(url)
    try:
        # Get streams info
        stream_url = f"{PIPED_API_BASE}/streams/{video_id}"
        metadata_url = f"{PIPED_API_BASE}/metadata/{video_id}"

        streams_res = requests.get(stream_url)
        meta_res = requests.get(metadata_url)

        if not streams_res.ok or not meta_res.ok:
            return {"error": "Failed to fetch video data"}

        data = streams_res.json()
        meta = meta_res.json()

        video_info = {
            "title": meta.get("title", "Unknown"),
            "thumbnail": meta.get("thumbnailUrl", "")
        }

        qualities = []
        for stream in data.get("videoStreams", []):
            if stream.get("container") == "mp4" and stream.get("videoOnly"):
                qualities.append({
                    "format_id": stream["url"],  # Direct URL becomes format_id now
                    "resolution": f"{stream['height']}p",
                    "ext": "mp4",
                    "tbr": stream["bitrate"]
                })

        qualities = sorted(qualities, key=lambda x: int(x["resolution"].replace("p", "")), reverse=True)

        if not qualities:
            return {"error": "No MP4 formats found"}

        return {"qualities": qualities, "video_info": video_info}

    except Exception as e:
        return {"error": f"API error: {str(e)}"}


def download_youtube_video(url, format_id, output_folder="downloads"):
    # Just redirect to direct video URL
    return {"download_url": format_id}
