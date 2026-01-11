"""
Flask API Server for UniDownload
Provides REST API endpoints for downloading media from various platforms
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import re
import glob
import json
from datetime import datetime
from youtube import YouTubeDownloader
from instagram import InstagramDownloader
from facebook import FacebookDownloader

app = Flask(__name__)
CORS(app)

# Initialize downloaders
youtube_dl = YouTubeDownloader()
instagram_dl = InstagramDownloader()
facebook_dl = FacebookDownloader()


def detect_platform(url):
    """Detect platform from URL"""
    url = url.lower()
    
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'instagram.com' in url:
        return 'instagram'
    elif 'facebook.com' in url or 'fb.watch' in url:
        return 'facebook'
    else:
        return 'unknown'


@app.route('/api/detect', methods=['POST'])
def detect():
    """Detect platform and get media info"""
    try:
        data = request.json
        url = data.get('url', '')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        platform = detect_platform(url)
        
        if platform == 'unknown':
            return jsonify({'error': 'Unsupported platform'}), 400
        
        # Get media info based on platform
        if platform == 'youtube':
            try:
                info = youtube_dl.get_video_info(url)
                if not info:
                    return jsonify({'error': 'Failed to fetch video information'}), 400
                
                # Get available formats
                formats = youtube_dl.display_formats(info, return_formats=True)
                
                # Format the formats for frontend
                formatted_formats = [{
                    'format_id': f['height'],
                    'label': f['display']
                } for f in formats]
                
                response = {
                    'platform': 'youtube',
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': formatted_formats,
                    'has_subtitles': bool(info.get('subtitles')),
                    'options': ['video', 'audio', 'playlist', 'subtitles', 'thumbnail']
                }
            except Exception as e:
                print(f"YouTube error: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'YouTube error: {str(e)}'}), 500
            
        elif platform == 'instagram':
            try:
                info = instagram_dl.get_media_info(url)
                if not info:
                    return jsonify({'error': 'Failed to fetch media information'}), 400
                
                media_type = instagram_dl.detect_media_type(url)
                
                response = {
                    'platform': 'instagram',
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'thumbnail': info.get('thumbnail', ''),
                    'media_type': media_type,
                    'options': ['post', 'audio']
                }
            except Exception as e:
                print(f"Instagram error: {str(e)}")
                return jsonify({'error': f'Instagram error: {str(e)}'}), 500
            
        elif platform == 'facebook':
            try:
                info = facebook_dl.get_video_info(url)
                if not info:
                    return jsonify({'error': 'Failed to fetch content information'}), 400
                
                content_type = facebook_dl.detect_content_type(url)
                
                response = {
                    'platform': 'facebook',
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'content_type': content_type,
                    'options': ['post', 'audio']
                }
            except Exception as e:
                print(f"Facebook error: {str(e)}")
                return jsonify({'error': f'Facebook error: {str(e)}'}), 500
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Server error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def download():
    """Download media with specified options"""
    try:
        data = request.json
        url = data.get('url', '')
        platform = data.get('platform', '')
        option = data.get('option', '')
        format_id = data.get('format_id', None)
        
        if not url or not platform:
            return jsonify({'error': 'URL and platform are required'}), 400
        
        # Get list of files before download
        before_files = set()
        for root, dirs, files in os.walk('downloads'):
            for file in files:
                before_files.add(os.path.join(root, file))
        
        # Process download based on platform and option
        if platform == 'youtube':
            if option == 'audio':
                youtube_dl.download_audio(url)
                message = 'Audio downloaded successfully'
            elif option == 'subtitles':
                youtube_dl.download_subtitles_only(url)
                message = 'Subtitles downloaded successfully'
            elif option == 'thumbnail':
                youtube_dl.download_thumbnail(url)
                message = 'Thumbnail downloaded successfully'
            elif option == 'playlist':
                youtube_dl.download_playlist(url)
                message = 'Playlist downloaded successfully'
            else:  # video
                if format_id:
                    # format_id is actually the quality height
                    youtube_dl.download_video(url, quality_height=int(format_id))
                else:
                    youtube_dl.download_video(url)
                message = 'Video downloaded successfully'
        
        elif platform == 'instagram':
            if option == 'audio':
                instagram_dl.download_audio(url)
                message = 'Audio downloaded successfully'
            else:  # post
                instagram_dl.download_post(url)
                message = 'Post downloaded successfully'
        
        elif platform == 'facebook':
            if option == 'audio':
                facebook_dl.download_audio(url)
                message = 'Audio downloaded successfully'
            else:  # post
                facebook_dl.download_post(url)
                message = 'Post downloaded successfully'
        
        # Get list of files after download
        after_files = set()
        for root, dirs, files in os.walk('downloads'):
            for file in files:
                after_files.add(os.path.join(root, file))
        
        # Find newly downloaded files
        new_files = after_files - before_files
        download_urls = []
        
        for file_path in new_files:
            # Convert to web-accessible path
            web_path = file_path.replace('\\', '/').replace('downloads/', '/api/files/')
            filename = os.path.basename(file_path)
            download_urls.append({
                'filename': filename,
                'url': web_path
            })
        
        return jsonify({
            'success': True, 
            'message': message,
            'files': download_urls
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'UniDownload API is running'})


@app.route('/api/files/<path:subpath>/<filename>')
def serve_file(subpath, filename):
    """Serve downloaded files"""
    try:
        directory = os.path.join('downloads', subpath)
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_file('static/index.html')


if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Get port from environment variable (for Render deployment)
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("UniDownload API Server")
    print("=" * 60)
    print(f"Server starting on port {port}")
    print("API Documentation:")
    print("  POST /api/detect  - Detect platform and get media info")
    print("  POST /api/download - Download media")
    print("  GET  /api/health  - Health check")
    print("=" * 60)
    
    # Use debug mode only in development
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
