"""
YouTube Downloader Module
Handles downloading videos and audio from YouTube using yt-dlp
"""

import os
import yt_dlp
import json


class YouTubeDownloader:
    """YouTube video and audio downloader with advanced features"""
    
    def __init__(self, download_path="downloads"):
        """
        Initialize YouTube downloader
        
        Args:
            download_path: Directory to save downloaded files
        """
        self.download_path = download_path
        self.default_format = "mp4"
        self._ensure_download_directory()
    
    def _ensure_download_directory(self):
        """Create download directory if it doesn't exist"""
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
            print(f"Created download directory: {self.download_path}")
    
    def set_output_folder(self):
        """Allow user to set custom output folder"""
        print("\nCurrent download folder:", self.download_path)
        new_path = input("Enter new download folder path (or press Enter to keep current): ").strip()
        
        if new_path:
            try:
                if not os.path.exists(new_path):
                    os.makedirs(new_path)
                self.download_path = new_path
                print(f"✓ Download folder set to: {self.download_path}")
            except Exception as e:
                print(f"✗ Error setting folder: {str(e)}")
        else:
            print("Keeping current folder.")
    
    def is_playlist(self, url):
        """Check if URL is a playlist"""
        return 'list=' in url or '/playlist' in url
    
    def get_video_info(self, url):
        """
        Fetch video information and available formats
        
        Args:
            url: YouTube video URL
            
        Returns:
            dict: Video information
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            print(f"Error fetching video info: {str(e)}")
            return None
    
    def display_formats(self, info, return_formats=False):
        """
        Display available video formats to user (YouTube-style)
        
        Args:
            info: Video information dictionary
            return_formats: If True, skip printing and just return formats
            
        Returns:
            list: List of available video formats with YouTube-style labels
        """
        if not info:
            return []
        
        if not return_formats:
            print(f"\nVideo Title: {info.get('title', 'Unknown')}")
            print(f"Duration: {info.get('duration', 0) // 60} minutes {info.get('duration', 0) % 60} seconds")
            print(f"Uploader: {info.get('uploader', 'Unknown')}")
            print("\n" + "=" * 60)
            print("Available Quality Options (with audio):")
            print("=" * 60)
        
        # Map actual heights to standard YouTube quality labels
        def get_quality_label(height):
            """Map actual video height to standard YouTube quality label"""
            if height >= 2160:
                return "2160p 4K"
            elif height >= 1440:
                return "1440p HD"
            elif height >= 1080:
                return "1080p HD"
            elif height >= 720:
                return "720p"
            elif height >= 480:
                return "480p"
            elif height >= 360:
                return "360p"
            elif height >= 240:
                return "240p"
            else:
                return "144p"
        
        # Get available qualities from formats
        available_qualities = set()
        for fmt in info.get('formats', []):
            height = fmt.get('height')
            vcodec = fmt.get('vcodec', 'none')
            if height and vcodec != 'none':
                available_qualities.add(height)
        
        # Map to standard quality labels and remove duplicates
        quality_map = {}
        for height in sorted(available_qualities, reverse=True):
            label = get_quality_label(height)
            # Use the highest actual height for each label
            if label not in quality_map:
                quality_map[label] = height
        
        # Create list of available formats
        video_formats = []
        for label in ["2160p 4K", "1440p HD", "1080p HD", "720p", "480p", "360p", "240p", "144p"]:
            if label in quality_map:
                video_formats.append({
                    'quality': label,
                    'height': quality_map[label],
                    'display': label
                })
        
        # Display options
        if not video_formats:
            if not return_formats:
                print("No video formats available")
            return []
        
        if not return_formats:
            for idx, fmt in enumerate(video_formats, 1):
                print(f"{idx}. {fmt['display']}")
            
            print("\nNote: All video downloads include audio (requires FFmpeg for HD+ qualities)")
        
        return video_formats
    
    def download_video(self, url, quality_height=None, output_format="mp4", download_subs=False, download_thumb=False, format_id=None):
        """
        Download video with specified quality (includes audio)
        
        Args:
            url: YouTube video URL
            quality_height: Desired quality height (e.g., 720, 1080)
            output_format: Output format (mp4, webm, mkv)
            download_subs: Download subtitles/captions
            download_thumb: Download thumbnail
            format_id: Specific format ID to download
        """
        output_template = os.path.join(self.download_path, '%(title)s.%(ext)s')
        
        # Format selection
        if format_id:
            format_string = format_id
        elif quality_height:
            format_string = f'bestvideo[height<={quality_height}]+bestaudio/best[height<={quality_height}]'
        else:
            format_string = 'bestvideo+bestaudio/best'
        
        ydl_opts = {
            'format': format_string,
            'outtmpl': output_template,
            'merge_output_format': output_format,
            'progress_hooks': [self._download_progress_hook],
        }
        
        # Add subtitle options
        if download_subs:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = ['en', 'en-US', 'en-GB']
            ydl_opts['subtitlesformat'] = 'srt'
        
        # Add thumbnail option
        if download_thumb:
            ydl_opts['writethumbnail'] = True
        
        try:
            print(f"\nDownloading video with audio...")
            if download_subs:
                print("+ Downloading subtitles")
            if download_thumb:
                print("+ Downloading thumbnail")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✓ Video downloaded successfully!")
        except Exception as e:
            error_msg = str(e)
            print(f"\n✗ Error downloading video: {error_msg}")
            
            # Check if it's an FFmpeg error
            if 'ffmpeg' in error_msg.lower():
                print("\n⚠ FFmpeg is required to merge video and audio streams!")
                print("\nInstall FFmpeg:")
                print("  Option 1: winget install ffmpeg")
                print("  Option 2: Download from https://www.gyan.dev/ffmpeg/builds/")
                print("            Extract and add to PATH")
                print("\nAfter installing, restart your terminal and try again.")
    
    def download_playlist(self, url, quality_height=None, output_format="mp4", download_subs=False):
        """
        Download entire playlist
        
        Args:
            url: YouTube playlist URL
            quality_height: Desired quality height
            output_format: Output format (mp4, webm, mkv)
            download_subs: Download subtitles
        """
        output_template = os.path.join(self.download_path, '%(playlist)s', '%(playlist_index)s - %(title)s.%(ext)s')
        
        if quality_height:
            format_string = f'bestvideo[height<={quality_height}]+bestaudio/best[height<={quality_height}]'
        else:
            format_string = 'bestvideo+bestaudio/best'
        
        ydl_opts = {
            'format': format_string,
            'outtmpl': output_template,
            'merge_output_format': output_format,
            'progress_hooks': [self._download_progress_hook],
            'ignoreerrors': True,  # Continue on errors
        }
        
        if download_subs:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = ['en', 'en-US', 'en-GB']
            ydl_opts['subtitlesformat'] = 'srt'
        
        try:
            print(f"\nDownloading playlist...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                playlist_title = info.get('title', 'Unknown Playlist')
                video_count = len(info.get('entries', []))
                
                print(f"Playlist: {playlist_title}")
                print(f"Videos: {video_count}")
                
                confirm = input("\nContinue with download? (y/n): ").strip().lower()
                if confirm == 'y':
                    ydl.download([url])
                    print("\n✓ Playlist downloaded successfully!")
                else:
                    print("Download cancelled.")
        except Exception as e:
            print(f"\n✗ Error downloading playlist: {str(e)}")
    
    def batch_download(self, urls, quality_height=None, output_format="mp4"):
        """
        Download multiple videos from a list of URLs
        
        Args:
            urls: List of YouTube video URLs
            quality_height: Desired quality height
            output_format: Output format (mp4, webm, mkv)
        """
        print(f"\nBatch downloading {len(urls)} video(s)...")
        
        for idx, url in enumerate(urls, 1):
            print(f"\n[{idx}/{len(urls)}] Processing: {url}")
            try:
                self.download_video(url, quality_height, output_format)
            except Exception as e:
                print(f"Failed to download {url}: {str(e)}")
                continue
        
        print("\n✓ Batch download completed!")
    
    def download_thumbnail(self, url):
        """
        Download only the thumbnail
        
        Args:
            url: YouTube video URL
        """
        output_template = os.path.join(self.download_path, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'skip_download': True,
            'writethumbnail': True,
            'outtmpl': output_template,
        }
        
        try:
            print(f"\nDownloading thumbnail...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✓ Thumbnail downloaded successfully!")
        except Exception as e:
            print(f"\n✗ Error downloading thumbnail: {str(e)}")
    
    def download_subtitles_only(self, url):
        """
        Download only subtitles/captions
        
        Args:
            url: YouTube video URL
        """
        output_template = os.path.join(self.download_path, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],  # Only English to avoid rate limiting
            'subtitlesformat': 'srt',
            'outtmpl': output_template,
        }
        
        try:
            print(f"\nDownloading English subtitles...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✓ Subtitles downloaded successfully!")
        except Exception as e:
            print(f"\n✗ Error downloading subtitles: {str(e)}")
    
    def download_audio(self, url):
        """
        Download audio only from YouTube video
        
        Args:
            url: YouTube video URL
        """
        output_template = os.path.join(self.download_path, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [self._download_progress_hook],
        }
        
        try:
            print(f"\nDownloading audio...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✓ Audio downloaded successfully!")
        except Exception as e:
            print(f"\n✗ Error downloading audio: {str(e)}")
    
    def _download_progress_hook(self, d):
        """Progress hook for download updates"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"\rProgress: {percent} | Speed: {speed} | ETA: {eta}", end='')
        elif d['status'] == 'finished':
            print(f"\rDownload completed, now processing...")
    
    def download(self, url):
        """
        Main download method with user interaction
        
        Args:
            url: YouTube video URL or playlist URL
        """
        # Check if it's a playlist
        if self.is_playlist(url):
            self._handle_playlist_download(url)
            return
        
        print("\nFetching video information...")
        info = self.get_video_info(url)
        
        if not info:
            print("Failed to fetch video information. Please check the URL.")
            return
        
        video_formats = self.display_formats(info)
        
        print("\n" + "=" * 60)
        print("Download Options:")
        print("=" * 60)
        print("V. Download Video (choose quality)")
        print("A. Download Audio Only (MP3)")
        print("T. Download Thumbnail Only")
        print("S. Download Subtitles Only")
        print("B. Back to main menu")
        print()
        
        choice = input("Enter your choice: ").strip().upper()
        
        if choice == "V":
            if not video_formats:
                print("No video formats available.")
                return
            
            print("\nSelect Quality:")
            for idx, fmt in enumerate(video_formats, 1):
                print(f"{idx}. {fmt['display']}")
            
            try:
                quality_choice = int(input("\nEnter quality number: ").strip())
                if 1 <= quality_choice <= len(video_formats):
                    selected_format = video_formats[quality_choice - 1]
                    
                    # Ask for additional options
                    print("\nAdditional Options:")
                    print("1. Format: MP4 (default)")
                    print("2. Format: WebM")
                    print("3. Format: MKV")
                    format_choice = input("Select format (press Enter for MP4): ").strip()
                    
                    format_map = {"1": "mp4", "2": "webm", "3": "mkv", "": "mp4"}
                    output_format = format_map.get(format_choice, "mp4")
                    
                    download_subs = input("Download subtitles? (y/n, default: n): ").strip().lower() == 'y'
                    download_thumb = input("Download thumbnail? (y/n, default: n): ").strip().lower() == 'y'
                    
                    self.download_video(url, selected_format['height'], output_format, download_subs, download_thumb)
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        elif choice == "A":
            self.download_audio(url)
        
        elif choice == "T":
            self.download_thumbnail(url)
        
        elif choice == "S":
            self.download_subtitles_only(url)
        
        elif choice == "B":
            return
        
        else:
            print("Invalid choice.")
    
    def _handle_playlist_download(self, url):
        """Handle playlist download with user options"""
        print("\n🎵 Playlist detected!")
        print("\n" + "=" * 60)
        print("Playlist Download Options:")
        print("=" * 60)
        print("1. Download entire playlist (video)")
        print("2. Download entire playlist (audio only)")
        print("3. Back to main menu")
        print()
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            # Get quality for playlist
            print("\nSelect Quality for all videos:")
            print("1. 1080p HD")
            print("2. 720p")
            print("3. 480p")
            print("4. 360p")
            print("5. Best available")
            
            quality_choice = input("\nEnter quality number: ").strip()
            quality_map = {"1": 1080, "2": 720, "3": 480, "4": 360, "5": None}
            quality = quality_map.get(quality_choice, 720)
            
            # Format selection
            print("\nSelect format:")
            print("1. MP4 (default)")
            print("2. WebM")
            print("3. MKV")
            format_choice = input("Enter format number (press Enter for MP4): ").strip()
            format_map = {"1": "mp4", "2": "webm", "3": "mkv", "": "mp4"}
            output_format = format_map.get(format_choice, "mp4")
            
            download_subs = input("Download subtitles for all videos? (y/n, default: n): ").strip().lower() == 'y'
            
            self.download_playlist(url, quality, output_format, download_subs)
        
        elif choice == "2":
            # Download playlist as audio
            self._download_playlist_audio(url)
        
        elif choice == "3":
            return
        
        else:
            print("Invalid choice.")
    
    def _download_playlist_audio(self, url):
        """Download playlist as audio only"""
        output_template = os.path.join(self.download_path, '%(playlist)s', '%(playlist_index)s - %(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [self._download_progress_hook],
            'ignoreerrors': True,
        }
        
        try:
            print(f"\nDownloading playlist as audio...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                playlist_title = info.get('title', 'Unknown Playlist')
                video_count = len(info.get('entries', []))
                
                print(f"Playlist: {playlist_title}")
                print(f"Videos: {video_count}")
                
                confirm = input("\nContinue with download? (y/n): ").strip().lower()
                if confirm == 'y':
                    ydl.download([url])
                    print("\n✓ Playlist audio downloaded successfully!")
                else:
                    print("Download cancelled.")
        except Exception as e:
            print(f"\n✗ Error downloading playlist: {str(e)}")
    
    def handle_batch_download(self):
        """Handle batch download from user input"""
        print("\n" + "=" * 60)
        print("Batch Download")
        print("=" * 60)
        print("Enter video URLs (one per line)")
        print("Enter 'done' when finished:")
        print()
        
        urls = []
        while True:
            url = input(f"URL {len(urls) + 1}: ").strip()
            if url.lower() == 'done':
                break
            if url:
                urls.append(url)
        
        if not urls:
            print("No URLs provided.")
            return
        
        print(f"\n{len(urls)} URL(s) added.")
        print("\nSelect Quality for all videos:")
        print("1. 1080p HD")
        print("2. 720p")
        print("3. 480p")
        print("4. 360p")
        print("5. Best available")
        
        quality_choice = input("\nEnter quality number: ").strip()
        quality_map = {"1": 1080, "2": 720, "3": 480, "4": 360, "5": None}
        quality = quality_map.get(quality_choice, 720)
        
        # Format selection
        print("\nSelect format:")
        print("1. MP4 (default)")
        print("2. WebM")
        print("3. MKV")
        format_choice = input("Enter format number (press Enter for MP4): ").strip()
        format_map = {"1": "mp4", "2": "webm", "3": "mkv", "": "mp4"}
        output_format = format_map.get(format_choice, "mp4")
        
        self.batch_download(urls, quality, output_format)

