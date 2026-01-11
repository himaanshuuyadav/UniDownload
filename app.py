"""
UniDownload - Universal Video/Image Downloader
Main application file
"""

import sys
from youtube import YouTubeDownloader
from instagram import InstagramDownloader
from facebook import FacebookDownloader


def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("          UniDownload - Universal Media Downloader")
    print("=" * 60)
    print()


def main_menu():
    """Display main menu and handle user selection"""
    print("\nSelect Platform:")
    print("1. YouTube")
    print("2. Instagram")
    print("3. Facebook")
    print("4. Threads (Coming Soon)")
    print("0. Exit")
    print()
    
    choice = input("Enter your choice: ").strip()
    return choice


def instagram_advanced_menu(downloader):
    """Instagram advanced options menu"""
    print("\n" + "=" * 60)
    print("Instagram Advanced Options")
    print("=" * 60)
    print("1. Set Custom Download Folder")
    print("2. Enable Browser Cookies (for private content)")
    print("3. Batch Download (Multiple URLs)")
    print("4. Back")
    print()
    
    choice = input("Enter your choice: ").strip()
    
    if choice == "1":
        downloader.set_output_folder()
    elif choice == "2":
        downloader.enable_cookies()
    elif choice == "3":
        downloader.handle_batch_download()
    elif choice == "4":
        return
    else:
        print("Invalid choice.")


def facebook_advanced_menu(downloader):
    """Facebook advanced options menu"""
    print("\n" + "=" * 60)
    print("Facebook Advanced Options")
    print("=" * 60)
    print("1. Set Custom Download Folder")
    print("2. Enable Browser Cookies (for private content)")
    print("3. Batch Download (Multiple URLs)")
    print("4. Back")
    print()
    
    choice = input("Enter your choice: ").strip()
    
    if choice == "1":
        downloader.set_output_folder()
    elif choice == "2":
        downloader.enable_cookies()
    elif choice == "3":
        downloader.handle_batch_download()
    elif choice == "4":
        return
    else:
        print("Invalid choice.")


def youtube_advanced_menu(downloader):
    """YouTube advanced options menu"""
    print("\n" + "=" * 60)
    print("YouTube Advanced Options")
    print("=" * 60)
    facebook_downloader = FacebookDownloader()
    print("1. Set Custom Download Folder")
    print("2. Batch Download (Multiple URLs)")
    print("3. Back")
    print()
    
    choice = input("Enter your choice: ").strip()
    
    if choice == "1":
        downloader.set_output_folder()
    elif choice == "2":
        downloader.handle_batch_download()
    elif choice == "3":
        return
    else:
        print("Invalid choice.")


def main():
    """Main application entry point"""
    print_banner()
    youtube_downloader = YouTubeDownloader()
    instagram_downloader = InstagramDownloader()
    facebook_downloader = FacebookDownloader()
    
    while True:
        choice = main_menu()
        
        if choice == "1":
            # YouTube downloader submenu
            print("\n" + "=" * 60)
            print("YouTube Options")
            print("=" * 60)
            print("1. Download Single Video/Playlist")
            print("2. Advanced Options")
            print("3. Back to Main Menu")
            print()
            
            yt_choice = input("Enter your choice: ").strip()
            
            if yt_choice == "1":
                url = input("\nEnter YouTube URL (video or playlist): ").strip()
                if url:
                    youtube_downloader.download(url)
                else:
                    print("Invalid URL. Please try again.")
            
            elif yt_choice == "2":
                youtube_advanced_menu(youtube_downloader)
            
            elif yt_choice == "3":
                continue
            
            else:
                print("Invalid choice.")
        
        elif choice == "2":
            # Instagram downloader submenu
            print("\n" + "=" * 60)
            print("Instagram Options")
            print("=" * 60)
            print("1. Download Post/Reel/Story")
            print("2. Advanced Options")
            print("3. Back to Main Menu")
            print()
            
            ig_choice = input("Enter your choice: ").strip()
            
            if ig_choice == "1":
                url = input("\nEnter Instagram URL (post/reel/story/IGTV): ").strip()
                if url:
                    instagram_downloader.download(url)
                else:
                    print("Invalid URL. Please try again.")
            
            elif ig_choice == "2":
                instagram_advanced_menu(instagram_downloader)
            
            elif ig_choice == "3":
                continue
            
            else:
                print("Invalid choice.")
        
        elif choice == "3":
            # Facebook downloader submenu
            print("\n" + "=" * 60)
            print("Facebook Options")
            print("=" * 60)
            print("1. Download Post/Video/Image")
            print("2. Advanced Options")
            print("3. Back to Main Menu")
            print()
            
            fb_choice = input("Enter your choice: ").strip()
            
            if fb_choice == "1":
                url = input("\nEnter Facebook URL (post/video/image): ").strip()
                if url:
                    facebook_downloader.download(url)
                else:
                    print("Invalid URL. Please try again.")
            
            elif fb_choice == "2":
                facebook_advanced_menu(facebook_downloader)
            
            elif fb_choice == "3":
                continue
            
            else:
                print("Invalid choice.")
        
        elif choice == "4":
            print("\nThreads downloader coming soon!")
        
        elif choice == "0":
            print("\nThank you for using UniDownload!")
            sys.exit(0)
        
        else:
            print("\nInvalid choice. Please try again.")
        
        print("\n" + "-" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting UniDownload...")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1)
