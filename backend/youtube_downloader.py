import yt_dlp
import os

def get_video_qualities(url):
    """Fetch available MP4 video qualities (video+audio merged)."""
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
            
            return {'qualities': quality_list}  # Wrap inside 'qualities' key
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
