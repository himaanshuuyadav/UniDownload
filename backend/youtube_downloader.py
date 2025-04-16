import yt_dlp
import requests
import json
import re
import os

COOKIE_FILE = os.path.join(os.path.dirname(__file__), "cookies", "youtube.cookies")


# Add your API key here after getting it from Google Developer Console
API_KEY = "AIzaSyBMEqA2fgrjz3C4W3LSDkww1bhxybh12Mc"

def is_valid_youtube_url(url):
    """Validate if the URL is a valid YouTube URL"""
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    youtube_regex_match = re.match(youtube_regex, url)
    return youtube_regex_match is not None

def extract_video_id(url):
    """Extract the video ID from a YouTube URL"""
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(6)
    return None

def get_video_qualities_api(url):
    """Fetch video information using YouTube Data API"""
    if not is_valid_youtube_url(url):
        return {'error': 'Invalid YouTube URL'}
    
    video_id = extract_video_id(url)
    if not video_id:
        return {'error': 'Could not extract video ID'}
    
    # Get basic video information from YouTube API
    api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={API_KEY}&part=snippet,contentDetails"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        
        if not data.get('items'):
            return {'error': 'Video not found or is private'}
        
        video_info = {
            'title': data['items'][0]['snippet']['title'],
            'thumbnail': data['items'][0]['snippet']['thumbnails']['high']['url']
        }
        
        # Now use yt-dlp to get available formats without downloading
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'cookiefile': COOKIE_FILE,
            'youtube_include_dash_manifest': False,
            'writeinfojson': True,
            'outtmpl': '/tmp/%(id)s.info.json'
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
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
                return {'qualities': qualities, 'video_info': video_info}
        except Exception as e:
            # If yt-dlp fails for formats, return only basic info
            return {'error': f'Format extraction failed: {str(e)}', 'video_info': video_info}
    
    except Exception as e:
        return {'error': f'API request failed: {str(e)}'}

# Legacy function using only yt-dlp (as fallback)
def get_video_qualities(url):
    """Fetch available MP4 video qualities (fallback to yt-dlp only)."""
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            
            quality_list = []
            for fmt in formats:
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none' and fmt['ext'] == 'mp4':
                    quality_list.append({
                        'format_id': fmt['format_id'],
                        'resolution': f"{fmt.get('height', 'Unknown')}p",
                        'ext': fmt['ext'],
                        'fps': fmt.get('fps', 'Unknown')
                    })
            
            return {'qualities': quality_list}
    except Exception as e:
        return {'error': str(e)}

def download_youtube_video(url, format_id, output_folder="downloads"):
    """Download YouTube video with highest audio merged."""
    os.makedirs(output_folder, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'format': f"{format_id}+bestaudio",  # Merge best audio
        'merge_output_format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return {'status': 'success'}
    except Exception as e:
        return {'error': str(e)}
