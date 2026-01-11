"""
Instagram Downloader Module
Handles downloading posts, reels, stories, and IGTV from Instagram using yt-dlp
"""

import os
import yt_dlp


class InstagramDownloader:
    """Instagram media downloader for posts, reels, stories, and IGTV"""
    
    def __init__(self, download_path="downloads/instagram"):
        """
        Initialize Instagram downloader
        
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
        print("Instagram Cookie Authentication")
        print("=" * 60)
        print("To download content that requires login, we can use")
        print("cookies from your browser where you're logged into Instagram.")
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
            print("Note: Make sure you're logged into Instagram in that browser.")
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
    
    def get_media_info(self, url):
        """
        Fetch Instagram media information
        
        Args:
            url: Instagram URL
            
        Returns:
            dict: Media information
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
                print(f"Error fetching media info: {error_msg}")
            return None
    
    def detect_media_type(self, url):
        """
        Detect type of Instagram content from URL
        
        Args:
            url: Instagram URL
            
        Returns:
            str: Media type (post, reel, story, tv, profile)
        """
        if '/reel/' in url or '/reels/' in url:
            return 'reel'
        elif '/stories/' in url:
            return 'story'
        elif '/tv/' in url or 'igtv' in url.lower():
            return 'tv'
        elif '/p/' in url:
            return 'post'
        else:
            return 'unknown'
    
    def download_post(self, url, download_thumbnail=False):
        """
        Download Instagram post (photo or video)
        
        Args:
            url: Instagram post URL
            download_thumbnail: Download thumbnail for videos
        """
        output_template = os.path.join(self.download_path, '%(uploader)s_%(id)s.%(ext)s')
        
        ydl_opts = self._get_base_ydl_opts()
        ydl_opts.update({
            'outtmpl': output_template,
            'progress_hooks': [self._download_progress_hook],
        })
        
        if download_thumbnail:
            ydl_opts['writethumbnail'] = True
        
        try:
            print(f"\nDownloading Instagram post...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Check if it's a carousel (multiple images/videos)
                if info and '_type' in info and info['_type'] == 'playlist':
                    print(f"✓ Downloaded {len(info.get('entries', []))} media items from carousel!")
                else:
                    print("\n✓ Post downloaded successfully!")
        except Exception as e:
            print(f"\n✗ Error downloading post: {str(e)}")
            print("\n⚠ If this is a private post or carousel:")
            print("  Go to Advanced Options → Enable Browser Cookies")
            print("📌 Make sure you're logged into Instagram in that browser.")
    
    def download_reel(self, url, quality='best'):
        """
        Download Instagram reel
        
        Args:
            url: Instagram reel URL
            quality: Video quality (best, 720p, 480p, 360p)
        """
        output_template = os.path.join(self.download_path, 'reels', '%(uploader)s_%(id)s.%(ext)s')
        
        # Create reels subdirectory
        reels_dir = os.path.join(self.download_path, 'reels')
        if not os.path.exists(reels_dir):
            os.makedirs(reels_dir)
        
        ydl_opts = self._get_base_ydl_opts()
        ydl_opts.update({
            'format': 'best',
            'outtmpl': output_template,
            'progress_hooks': [self._download_progress_hook],
        })
        
        try:
            print(f"\nDownloading Instagram reel...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✓ Reel downloaded successfully!")
        except Exception as e:
            print(f"\n✗ Error downloading reel: {str(e)}")
            self._show_instagram_help()
    
    def download_story(self, url):
        """
        Download Instagram story
        
        Args:
            url: Instagram story URL
        """
        output_template = os.path.join(self.download_path, 'stories', '%(uploader)s_%(id)s.%(ext)s')
        
        # Create stories subdirectory
        stories_dir = os.path.join(self.download_path, 'stories')
        if not os.path.exists(stories_dir):
            os.makedirs(stories_dir)
        
        ydl_opts = self._get_base_ydl_opts()
        ydl_opts.update({
            'outtmpl': output_template,
            'progress_hooks': [self._download_progress_hook],
        })
        
        try:
            print(f"\nDownloading Instagram story...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✓ Story downloaded successfully!")
        except Exception as e:
            print(f"\n✗ Error downloading story: {str(e)}")
            self._show_instagram_help()
    
    def download_igtv(self, url):
        """
        Download Instagram TV (IGTV) video
        
        Args:
            url: IGTV URL
        """
        output_template = os.path.join(self.download_path, 'igtv', '%(uploader)s_%(id)s.%(ext)s')
        
        # Create igtv subdirectory
        igtv_dir = os.path.join(self.download_path, 'igtv')
        if not os.path.exists(igtv_dir):
            os.makedirs(igtv_dir)
        
        ydl_opts = self._get_base_ydl_opts()
        ydl_opts.update({
            'format': 'best',
            'outtmpl': output_template,
            'progress_hooks': [self._download_progress_hook],
        })
        
        try:
            print(f"\nDownloading IGTV video...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✓ IGTV video downloaded successfully!")
        except Exception as e:
            print(f"\n✗ Error downloading IGTV: {str(e)}")
            self._show_instagram_help()
    
    def download_audio(self, url):
        """
        Download audio from Instagram video/reel
        
        Args:
            url: Instagram URL
        """
        output_template = os.path.join(self.download_path, 'audio', '%(uploader)s_%(id)s.%(ext)s')
        
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
        Download multiple Instagram URLs
        
        Args:
            urls: List of Instagram URLs
        """
        print(f"\nBatch downloading {len(urls)} item(s)...")
        
        for idx, url in enumerate(urls, 1):
            print(f"\n[{idx}/{len(urls)}] Processing: {url}")
            media_type = self.detect_media_type(url)
            
            try:
                if media_type == 'reel':
                    self.download_reel(url)
                elif media_type == 'story':
                    self.download_story(url)
                elif media_type == 'tv':
                    self.download_igtv(url)
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
    
    def _show_instagram_help(self):
        """Show help for Instagram authentication if needed"""
        print("\n⚠ Note: Some Instagram content may require authentication.")
        print("If you encounter errors, you may need to:")
        print("  1. Use yt-dlp with cookies from your browser")
        print("  2. Or download public content only")
    
    def download(self, url):
        """
        Main download method with auto-detection
        
        Args:
            url: Instagram URL
        """
        print("\nFetching media information...")
        info = self.get_media_info(url)
        
        if not info:
            print("Failed to fetch media information. Please check the URL.")
            print("\n📌 Make sure the content is public or you have access to it.")
            return
        
        # Detect media type
        media_type = self.detect_media_type(url)
        
        # Display media info
        uploader = info.get('uploader', 'Unknown')
        description = info.get('description', 'No description')
        likes = info.get('like_count', 0)
        comments = info.get('comment_count', 0)
        
        print("\n" + "=" * 60)
        print(f"Media Type: {media_type.upper()}")
        print(f"Uploader: {uploader}")
        if likes:
            print(f"Likes: {likes:,}")
        if comments:
            print(f"Comments: {comments:,}")
        if description and len(description) < 100:
            print(f"Description: {description}")
        print("=" * 60)
        
        print("\nDownload Options:")
        print("=" * 60)
        print("1. Download Media (Best Quality)")
        print("2. Download Audio Only (MP3)")
        print("3. Download with Thumbnail")
        print("4. Back to main menu")
        print()
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            if media_type == 'reel':
                self.download_reel(url)
            elif media_type == 'story':
                self.download_story(url)
            elif media_type == 'tv':
                self.download_igtv(url)
            else:
                self.download_post(url)
        
        elif choice == "2":
            self.download_audio(url)
        
        elif choice == "3":
            self.download_post(url, download_thumbnail=True)
        
        elif choice == "4":
            return
        
        else:
            print("Invalid choice.")
    
    def handle_batch_download(self):
        """Handle batch download from user input"""
        print("\n" + "=" * 60)
        print("Instagram Batch Download")
        print("=" * 60)
        print("Enter Instagram URLs (one per line)")
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
