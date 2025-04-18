from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from flask_cors import CORS
from youtube_downloader import get_video_qualities_api, download_youtube_video


app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/style/<path:path>')
def send_style(path):
    return send_from_directory(os.path.join(app.static_folder, 'style'), path)

@app.route('/get_qualities', methods=['POST'])
def get_qualities():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    result = get_video_qualities_api(url)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    format_id = data.get('format_id')

    if not url or not format_id:
        return jsonify({'error': 'Missing URL or format ID'}), 400

    result = download_youtube_video(url, format_id)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)
