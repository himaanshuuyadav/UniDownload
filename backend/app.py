from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_downloader import get_video_qualities_api, download_youtube_video

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "UniDownload Backend Running"

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
