import yt_dlp
import os
import requests
import json
import re

# ✅ Absolute path to your cookie file
COOKIE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "cookies", "youtube.cookies"))

# Add your API key here if using YouTube Data API
API_KEY = "AIzaSyBMEqA2fgrjz3C4W3LSDkww1bhxybh12Mc"

def is_valid_youtube_url(url):
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    return re.match(youtube_regex, url) is not None

def extract_video_id(url):
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    match = re.match(youtube_regex, url)
    return match.group(6) if match else None

def get_video_qualities_api(url):
    if not is_valid_youtube_url(url):
        return {'error': 'Invalid YouTube URL'}

    video_id = extract_video_id(url)
    if not video_id:
        return {'error': 'Could not extract video ID'}

    print("Cookie file being used:", COOKIE_FILE)
    print("Cookie file exists:", os.path.exists(COOKIE_FILE))

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'cookiefile': COOKIE_FILE,
            'youtube_include_dash_manifest': False,
            'writeinfojson': True,
            'outtmpl': '/tmp/%(id)s.info.json',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.youtube.com/',
                'Cookie': 'SID=g.a000vQjmU-7RWONRMFY_Yax7MmkSteBz5FooSEsZ8JQbAhY3ZFMccPmGHTXVSZQ6EC_xby-nlwACgYKAWUSARMSFQHGX2Mi-m7fwxmvfp7abpAPUXJDJRoVAUF8yKo4GTIvZ64D4QEPAps0eVNs0076; SAPISID=ufEADAPBA9UdNGl-/Af_0mS7cuNECo8eOk'
            }

        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

            video_info = {
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail', '')
            }

            best_qualities = {}
            for fmt in formats:
                # ✅ Simplified format filter
                if fmt.get("ext") == "mp4" and fmt.get("format_id") and fmt.get("vcodec") != "none":
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
                return {'error': 'No valid MP4 formats found for this video'}

            return {'qualities': qualities, 'video_info': video_info}

    except yt_dlp.utils.DownloadError as e:
        print("yt-dlp error:", e)
        return {'error': f'Format extraction failed: {str(e)}'}

    except Exception as e:
        print("General exception:", e)
        return {'error': f'API request failed: {str(e)}'}

def download_youtube_video(url, format_id, output_folder="downloads"):
    os.makedirs(output_folder, exist_ok=True)

    print("Downloading video:", url)
    print("Using format_id:", format_id)

    ydl_opts = {
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'format': format_id,
        'merge_output_format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return {'status': 'success'}
    except Exception as e:
        print("Download error details:", e)
        return {'error': f'Download failed: {str(e)}'}

