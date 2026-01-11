"""
Facebook Downloader Module
Handles downloading videos, images, and posts from Facebook using yt-dlp
"""

import os
import yt_dlp


class FacebookDownloader:
    """Facebook video downloader"""
    
    def __init__(self, download_path="downloads/facebook"):
        """
        Initialize Facebook downloader
        
        Args:
            download_path: Directory to save downloaded files
        """
        self.download_path = download_path
        self.use_cookies = False
        self.cookies_browser = None
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
    
    def enable_cookies(self):
        """Enable cookies from browser for authentication"""
        print("\n" + "=" * 60)
        print("Facebook Cookie Authentication")
        print("=" * 60)
        print("To download content that requires login, we can use")
        print("cookies from your browser where you're logged into Facebook.")
        print()
        print("⚠ IMPORTANT: CLOSE your browser completely before downloading!")
        print("Browsers lock cookies while running.")
        print()
        print("Available browsers:")
        print("1. Chrome")
        print("2. Firefox")
        print("3. Edge")
        print("4. Opera")
        print("5. Brave")
        print("6. Disable cookies (use without login)")
        print()
        
        choice = input("Select browser (or press Enter to skip): ").strip()
        
        browser_map = {
            "1": "chrome",
            "2": "firefox",
            "3": "edge",
            "4": "opera",
            "5": "brave"
        }
        
        if choice in browser_map:
            self.use_cookies = True
            self.cookies_browser = browser_map[choice]
            print(f"✓ Cookies enabled from {browser_map[choice].capitalize()}")
            print("Note: Make sure you're logged into Facebook in that browser.")
        elif choice == "6":
            self.use_cookies = False
            self.cookies_browser = None
            print("✓ Cookies disabled")
        else:
            print("Skipped cookie setup.")
    
    def _get_base_ydl_opts(self):
        """Get base yt-dlp options with cookies if enabled"""
        opts = {}
        if self.use_cookies and self.cookies_browser:
            opts['cookiesfrombrowser'] = (self.cookies_browser,)
        return opts
    
    def detect_content_type(self, url):
        """
        Detect type of Facebook content from URL or by fetching info
        
        Args:
            url: Facebook URL
            
        Returns:
            str: Content type (video, image, album, unknown)
        """
        try:
            info = self.get_video_info(url)
            if not info:
                return 'unknown'
            
            # Check if it's a video
            if info.get('ext') in ['mp4', 'webm', 'mkv'] or 'video' in str(info.get('_type', '')):
                return 'video'
            # Check if it's an image
            elif info.get('ext') in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                return 'image'
            # Check if it's an album/carousel
            elif info.get('_type') == 'playlist':
                return 'album'
            else:
                return 'video'  # Default to video
        except:
            return 'video'
    
    def get_video_info(self, url):
        """
        Fetch Facebook video information
        
        Args:
            url: Facebook URL
            
        Returns:
            dict: Video information
        """
        ydl_opts = self._get_base_ydl_opts()
        ydl_opts.update({
            'quiet': True,
            'no_warnings': True,
        })
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            error_msg = str(e)
            if "cookie database" in error_msg.lower():
                print(f"\n⚠ Cookie Access Error!")
                print(f"Please CLOSE your {self.cookies_browser.capitalize() if self.cookies_browser else 'browser'} browser completely and try again.")
                print(f"Browsers lock their cookie database while running.")
                print(f"\nAlternatively, disable cookies in Advanced Options.")
            elif "dpapi" in error_msg.lower() or "decrypt" in error_msg.lower():
                print(f"\n⚠ Cookie Encryption Error!")
                print(f"{self.cookies_browser.capitalize() if self.cookies_browser else 'Your browser'} uses encryption that yt-dlp can't decrypt.")
                print(f"\nSolutions:")
                print(f"  1. Try Firefox instead (recommended) - it doesn't encrypt cookies")
                print(f"  2. Disable cookies and try downloading without login")
                print(f"  3. Some public content works without authentication")
            else:
                print(f"Error fetching video info: {error_msg}")
            return None
    
    def download_image(self, url):
        """
        Download image from Facebook post
        
        Args:
            url: Facebook post URL with image
        """
        output_template = os.path.join(self.download_path, 'images', '%(title)s_%(id)s.%(ext)s')
        
        # Create images subdirectory
        images_dir = os.path.join(self.download_path, 'images')
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        ydl_opts = self._get_base_ydl_opts()
        ydl_opts.update({
            'outtmpl': output_template,
            'progress_hooks': [self._download_progress_hook],
        })
        
        try:
            print(f"\nDownloading Facebook image...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✓ Image downloaded successfully!")
        except Exception as e:
            print(f"\n✗ Error downloading image: {str(e)}")
            self._show_facebook_help()
    
    def download_post(self, url):
        """
        Download Facebook post (handles images, videos, or albums)
        
        Args:
            url: Facebook post URL
        """
        output_template = os.path.join(self.download_path, '%(title)s_%(id)s.%(ext)s')
        
        ydl_opts = self._get_base_ydl_opts()
        ydl_opts.update({
            'outtmpl': output_template,
            'progress_hooks': [self._download_progress_hook],
        })
        
        try:
            print(f"\nDownloading Facebook post...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Check if it's an album with multiple items
                if info and '_type' in info and info['_type'] == 'playlist':
                    print(f"\n✓ Downloaded {len(info.get('entries', []))} item(s) from album!")
                else:
                    print("\n✓ Post downloaded successfully!")
        except Exception as e:
            print(f"\n✗ Error downloading post: {str(e)}")
            self._show_facebook_help()
    
    def download_video(self, url, quality='best'):
        """
        Download Facebook video
        
        Args:
            url: Facebook video URL
            quality: Video quality preference
        """
        output_template = os.path.join(self.download_path, '%(title)s_%(id)s.%(ext)s')
        
        ydl_opts = self._get_base_ydl_opts()
        ydl_opts.update({
            'format': 'best',
            'outtmpl': output_template,
            'progress_hooks': [self._download_progress_hook],
        })
        
        try:
            print(f"\nDownloading Facebook video...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✓ Video downloaded successfully!")
        except Exception as e:
            print(f"\n✗ Error downloading video: {str(e)}")
            self._show_facebook_help()
    
    def download_audio(self, url):
        """
        Download audio from Facebook video
        
        Args:
            url: Facebook URL
        """
        output_template = os.path.join(self.download_path, 'audio', '%(title)s_%(id)s.%(ext)s')
        
        # Create audio subdirectory
        audio_dir = os.path.join(self.download_path, 'audio')
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        
        ydl_opts = self._get_base_ydl_opts()
        ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [self._download_progress_hook],
        })
        
        try:
            print(f"\nDownloading audio...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✓ Audio downloaded successfully!")
        except Exception as e:
            print(f"\n✗ Error downloading audio: {str(e)}")
    
    def batch_download(self, urls):
        """
        Download multiple Facebook posts/videos
        
        Args:
            urls: List of Facebook URLs
        """
        print(f"\nBatch downloading {len(urls)} item(s)...")
        
        for idx, url in enumerate(urls, 1):
            print(f"\n[{idx}/{len(urls)}] Processing: {url}")
            try:
                content_type = self.detect_content_type(url)
                if content_type == 'image':
                    self.download_image(url)
                else:
                    self.download_post(url)
            except Exception as e:
                print(f"Failed to download {url}: {str(e)}")
                continue
        
        print("\n✓ Batch download completed!")
    
    def _download_progress_hook(self, d):
        """Progress hook for download updates"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"\rProgress: {percent} | Speed: {speed} | ETA: {eta}", end='')
        elif d['status'] == 'finished':
            print(f"\rDownload completed, now processing...")
    
    def _show_facebook_help(self):
        """Show help for Facebook download issues"""
        print("\n⚠ Note: Some Facebook content requires authentication.")
        print("If you encounter 'registered users only' errors:")
        print("  1. Go to Advanced Options → Enable Browser Cookies")
        print("  2. Make sure you're logged into Facebook in that browser")
        print("  3. Try downloading again")
        print()
        print("Other tips:")
        print("  - Make sure the content is public")
        print("  - Try using a direct Facebook post/video URL")
        print("  - Some region-restricted content may not be downloadable")
    
    def download(self, url):
        """
        Main download method with user interaction
        
        Args:
            url: Facebook post/video URL
        """
        print("\nFetching content information...")
        info = self.get_video_info(url)
        
        if not info:
            print("Failed to fetch content information. Please check the URL.")
            self._show_facebook_help()
            return
        
        # Detect content type
        content_type = self.detect_content_type(url)
        
        # Display content info
        title = info.get('title', 'Unknown')
        uploader = info.get('uploader', 'Unknown')
        duration = info.get('duration', 0)
        
        print("\n" + "=" * 60)
        print(f"Content Type: {content_type.upper()}")
        print(f"Title: {title}")
        print(f"Uploader: {uploader}")
        if duration and content_type == 'video':
            print(f"Duration: {duration // 60:.0f} minutes {duration % 60} seconds")
        
        # Check if it's an album
        if info.get('_type') == 'playlist':
            entries_count = len(info.get('entries', []))
            print(f"Album Items: {entries_count}")
        
        print("=" * 60)
        
        print("\nDownload Options:")
        print("=" * 60)
        
        if content_type == 'video' or content_type == 'album':
            print("1. Download Post/Video (Best Quality)")
            print("2. Download Audio Only (MP3)")
            print("3. Back to main menu")
        else:
            print("1. Download Post/Image")
            print("2. Back to main menu")
        
        print()
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            if content_type == 'image':
                self.download_image(url)
            else:
                self.download_post(url)
        
        elif choice == "2":
            if content_type == 'video' or content_type == 'album':
                self.download_audio(url)
            else:
                return
        
        elif choice == "3":
            return
        
        else:
            print("Invalid choice.")
    
    def handle_batch_download(self):
        """Handle batch download from user input"""
        print("\n" + "=" * 60)
        print("Facebook Batch Download")
        print("=" * 60)
        print("Enter Facebook URLs (posts/videos/images, one per line)")
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
        confirm = input("Continue with batch download? (y/n): ").strip().lower()
        
        if confirm == 'y':
            self.batch_download(urls)
        else:
            print("Batch download cancelled.")
