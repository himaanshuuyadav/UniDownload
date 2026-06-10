"""
UniDownload Backend — Python Flask + yt-dlp

A universal media downloader powered by yt-dlp.

Extracts and downloads media from supported websites using yt-dlp's
extraction APIs.  No DOM scraping, no browser automation, no login handling.

Communication protocol:
  All requests and responses use JSON.
  The extension sends the URL; the backend returns metadata and triggers
  yt-dlp downloads to local directories.

Architecture:
  1. yt-dlp's Instagram extractor has known gaps — it discards image-only
     entries from carousels and raises errors on single-image posts.
  2. The three monkey patches below fix these gaps WITHOUT touching the site
     DOM or using any extraction method other than yt-dlp.
  3. After patching, all extraction flows through yt-dlp's own internal code.
  4. Platform detection in classify_url() makes the backend extensible to
     YouTube, TikTok, X/Twitter, and other yt-dlp supported websites.
"""

import os, re, glob, json, datetime
from flask import Flask, request, jsonify

import yt_dlp
from yt_dlp.utils import traverse_obj, bug_reports_message
from yt_dlp.extractor.instagram import (
    InstagramBaseIE, InstagramIE, InstagramIOSIE,
    ExtractorError, _pk_to_id,
)

# ====================================================================
# MONKEY PATCH 1 — _extract_nodes
#
# What yt-dlp does:   skips image nodes (continues past them).
# What we need:        yield image entries using display_url as the URL.
#
# Strategy: wrap the original so video nodes still use yt-dlp's logic,
# and image nodes get a synthetic entry with the image URL.
# ====================================================================

_orig_extract_nodes = InstagramBaseIE._extract_nodes


def _patched_extract_nodes(self, nodes, is_direct=False):
    for idx, node in enumerate(nodes, start=1):
        is_video = node.get('__typename') == 'GraphVideo' or node.get('is_video') is True
        is_image = node.get('__typename') == 'GraphImage' or node.get('is_video') is False

        if is_video:
            yield from _orig_extract_nodes(self, [node], is_direct)

        elif is_image and is_direct:
            image_url = (node.get('display_url')
                         or node.get('thumbnail_src')
                         or node.get('display_src'))
            if not image_url:
                continue

            image_id = node.get('shortcode') or node.get('id')
            if not image_id:
                continue

            info = {
                'id': image_id,
                'url': image_url,
                'title': node.get('title') or f'Image {idx}',
                'width': traverse_obj(node, ('dimensions', 'width')),
                'height': traverse_obj(node, ('dimensions', 'height')),
                'http_headers': {'Referer': 'https://www.instagram.com/'},
            }

            yield {
                **info,
                'description': traverse_obj(
                    node, ('edge_media_to_caption', 'edges', 0, 'node', 'text'),
                    expected_type=str),
                'thumbnail': image_url,
                'timestamp': int_or_none(node.get('taken_at_timestamp')),
                'like_count': InstagramBaseIE._get_count(
                    self, node, 'likes', 'preview_like'),
            }

        elif is_image and not is_direct:
            image_id = node.get('shortcode') or node.get('id')
            if not image_id:
                continue
            yield {
                '_type': 'url',
                'ie_key': 'Instagram',
                'id': image_id,
                'url': 'https://instagram.com/p/' + image_id,
            }


InstagramBaseIE._extract_nodes = _patched_extract_nodes


# ====================================================================
# MONKEY PATCH 2 — _extract_product_media
#
# What yt-dlp does:   returns {} for non-video items (images).
# What we need:        return image URL from image_versions2.candidates.
# ====================================================================

_orig_extract_product_media = InstagramBaseIE._extract_product_media


def _patched_extract_product_media(self, product_media):
    dash_manifest_raw = product_media.get('video_dash_manifest')
    videos_list = product_media.get('video_versions')
    if videos_list or dash_manifest_raw:
        return _orig_extract_product_media(self, product_media)

    candidates = traverse_obj(
        product_media, ('image_versions2', 'candidates')) or []
    if not candidates:
        return {}

    thumbnails = []
    for c in candidates:
        if c.get('url'):
            thumbnails.append({
                'url': c['url'],
                'width': c.get('width'),
                'height': c.get('height'),
            })

    best = max(candidates, key=lambda c: (c.get('width') or 0) * (c.get('height') or 0))
    media_id = (product_media.get('code')
                or InstagramBaseIE._pk_to_id(product_media.get('pk')))

    return {
        'id': media_id,
        'url': best.get('url'),
        'width': best.get('width'),
        'height': best.get('height'),
        'thumbnails': thumbnails,
    }


InstagramBaseIE._extract_product_media = _patched_extract_product_media


# ====================================================================
# MONKEY PATCH 3 — _real_extract  (single-image fix)
# ====================================================================

def _patched_real_extract(self, url):
    video_id, clean_url = InstagramIE._match_valid_url(url).group('id', 'url')

    try:
        return _orig_real_extract(self, url)
    except ExtractorError as e:
        if 'no video' not in str(e).lower():
            raise
    except Exception:
        pass

    media = {}

    if self._get_cookies(clean_url).get('sessionid'):
        info = self._download_json(
            f'{self._API_BASE_URL}/media/{_pk_to_id(video_id)}/info/',
            video_id, fatal=False, errnote='',
            note='Downloading video info', headers=self._api_headers)
        if info and info.get('items'):
            media.update(info['items'][0])
            return self._extract_product(media)

    csrf_token = self._get_cookies('https://www.instagram.com').get('csrftoken')
    if csrf_token:
        csrf_token = csrf_token.value

    variables = {
        'shortcode': video_id,
        'child_comment_count': 3,
        'fetch_comment_count': 40,
        'parent_comment_count': 24,
        'has_threaded_comments': True,
    }

    general_info = self._download_json(
        'https://www.instagram.com/graphql/query/', video_id, fatal=False,
        errnote=False, headers={
            **self._api_headers,
            'X-CSRFToken': csrf_token or '',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': clean_url,
        }, query={
            'doc_id': '8845758582119845',
            'variables': json.dumps(variables, separators=(',', ':')),
        })

    if general_info:
        media = traverse_obj(
            general_info, ('data', 'xdt_shortcode_media', {dict})) or {}

    if not media:
        webpage = self._download_webpage(
            clean_url + '/embed/', video_id,
            note='Downloading embed webpage', fatal=False) or ''
        additional_data = self._search_json(
            r'window\.__additionalDataLoaded\s*\(\s*[^,]+,',
            webpage, 'additional data', video_id, fatal=False)
        if additional_data:
            media.update(traverse_obj(
                additional_data, ('items', 0),
                ('graphql', 'shortcode_media'),
                'shortcode_media', expected_type=dict) or {})

    if not media:
        self.raise_login_required(
            'Requested content is not available, rate-limit reached, '
            'or login required')

    image_url = (media.get('display_url')
                 or media.get('display_src')
                 or self._og_search_thumbnail(webpage))
    if not image_url:
        raise ExtractorError('Could not find image URL', expected=True)

    username = traverse_obj(media, ('owner', 'username'))
    description = (
        traverse_obj(media,
                     ('edge_media_to_caption', 'edges', 0, 'node', 'text'),
                     expected_type=str)
        or media.get('caption'))

    return self.playlist_result(
        [{
            'id': video_id,
            'url': image_url,
            'title': f'Image by {username}' if username else f'Instagram {video_id}',
            'description': description,
            'width': traverse_obj(media, ('dimensions', 'width')),
            'height': traverse_obj(media, ('dimensions', 'height')),
            'thumbnail': image_url,
            'http_headers': {'Referer': 'https://www.instagram.com/'},
            'timestamp': traverse_obj(
                media, 'taken_at_timestamp', expected_type=int_or_none),
        }],
        video_id,
        format_field(username, None, 'Post by %s'),
        description,
    )


_orig_real_extract = InstagramIE._real_extract
InstagramIE._real_extract = _patched_real_extract
InstagramIOSIE._real_extract = _patched_real_extract


# ====================================================================
# Flask app
# ====================================================================

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, 'downloads')
MEDIA_DIR = os.path.join(DOWNLOADS_DIR, 'media')
VIDEOS_DIR = os.path.join(DOWNLOADS_DIR, 'videos')
DEBUG_DIR = os.path.join(BASE_DIR, 'debug')

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)

YTDL_COMMON = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
}


# -----------------------------------------------------------------------
# help from yt_dlp
# -----------------------------------------------------------------------
def int_or_none(v):
    if v is None:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def format_field(obj, field, template):
    val = obj.get(field) if isinstance(obj, dict) else None
    if val:
        return template.replace('%s', val)
    return None


# -----------------------------------------------------------------------
# helpers
# -----------------------------------------------------------------------

def detect_platform(url):
    """Return a short platform identifier from the URL.
       Currently supports Instagram; extend for YouTube, TikTok, etc."""
    if 'instagram.com' in url:
        return 'instagram'
    # Future: youtube.com -> 'youtube', tiktok.com -> 'tiktok', etc.
    return 'unknown'


def classify_url(url):
    if '/reel/' in url:
        return 'reel'
    if '/p/' in url:
        return 'post'
    return None


def timestamp():
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


# -----------------------------------------------------------------------
# item extraction from an entry
# -----------------------------------------------------------------------

def extract_url_from_entry(entry):
    if not entry or not isinstance(entry, dict):
        return None, None, None

    keys = list(entry.keys())
    print('    ENTRY KEYS:', keys)

    # 1. Direct url field
    direct_url = entry.get('url') or ''
    if direct_url and direct_url.startswith('http') and 'instagram.com/p/' not in direct_url:
        ext = entry.get('ext') or ''
        mtype = 'video' if ext in ('mp4', 'webm', 'mov') else 'image'
        if not ext:
            if '.mp4' in direct_url or '.webm' in direct_url:
                ext = 'mp4'
                mtype = 'video'
            elif '.jpg' in direct_url or '.png' in direct_url or '.webp' in direct_url:
                ext = 'jpg'
                mtype = 'image'
        return direct_url, mtype, ext or 'jpg'

    # 2. formats array
    formats = entry.get('formats') or []
    if formats and isinstance(formats, list):
        print('    FORMAT COUNT: ' + str(len(formats)))
        for fi, fmt in enumerate(formats[:5]):
            print('    FORMAT ' + str(fi) + ': ' + json.dumps({
                'format_id': fmt.get('format_id'),
                'ext': fmt.get('ext'),
                'width': fmt.get('width'),
                'height': fmt.get('height'),
                'tbr': fmt.get('tbr'),
            }, default=str))

        best = None
        best_score = -1
        for f in formats:
            url = f.get('url') or ''
            if not url or not url.startswith('http'):
                continue
            w = f.get('width') or 0
            h = f.get('height') or 0
            tbr = f.get('tbr') or 0
            resolution = w * h
            score = (resolution, tbr)
            if not best or score > best_score:
                best = f
                best_score = score

        if best:
            ext = entry.get('ext') or best.get('ext') or ''
            vcodec = best.get('vcodec')
            mtype = 'video' if (vcodec or ext in ('mp4', 'webm', 'mov')) else 'image'
            if not ext and mtype == 'video':
                ext = 'mp4'
            elif not ext:
                ext = 'jpg'
            print('    BEST FORMAT: ' + json.dumps({
                'format_id': best.get('format_id'),
                'ext': ext,
                'width': best.get('width'),
                'height': best.get('height'),
            }, default=str))
            return best['url'], mtype, ext

    # 3. _type == 'url'
    if entry.get('_type') == 'url':
        print('    SKIP: _type=url entry (needs re-resolution)')
        return None, None, None

    # 4. thumbnail fallback
    thumb = (entry.get('thumbnail')
             or (entry.get('thumbnails') and entry['thumbnails'][0].get('url'))
             or '')
    if thumb and thumb.startswith('http'):
        print('    FALLBACK: using thumbnail as URL')
        return thumb, 'image', 'jpg'

    return None, None, None


# -----------------------------------------------------------------------
# POST /analyze
# -----------------------------------------------------------------------

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True) or {}
    url = (data.get('url') or '').strip()

    if not url:
        return jsonify({'success': False, 'error': 'No URL provided.'})

    # Currently Instagram only; will extend as more platforms are added.
    post_type = classify_url(url)
    platform = detect_platform(url)
    print('PLATFORM:', platform)

    if not post_type:
        return jsonify({
            'success': False,
            'error': 'Not a supported URL. Currently supports Instagram /p/ and /reel/ links.'
        })

    # --- yt-dlp extraction ---
    try:
        with yt_dlp.YoutubeDL(YTDL_COMMON) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'yt-dlp extraction failed: {str(e)}'
        })

    # --- save raw debug.json ---
    try:
        debug_path = os.path.join(DEBUG_DIR, 'debug.json')
        with open(debug_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, default=str, ensure_ascii=False)
        print('DEBUG saved to:', debug_path)
    except Exception as dump_err:
        print('DEBUG save error:', dump_err)

    # --- inspect structure ---
    type_val = info.get('_type')
    top_keys = list(info.keys())
    print('TYPE:', type_val)
    print('TOP LEVEL KEYS:', top_keys)

    media_items = []
    extracted_url_count = 0

    # --- PARSING LOGIC ---
    if type_val == 'playlist':
        entries = info.get('entries') or []
        if hasattr(entries, '__iter__') and not isinstance(entries, list):
            entries = list(entries)
        entry_count = len(entries)
        print('ENTRY COUNT:', entry_count)

        if entry_count > 0:
            first_entry = entries[0]
            if isinstance(first_entry, dict):
                print('FIRST ENTRY KEYS:', list(first_entry.keys()))
        else:
            print('ENTRIES: empty list')

        for i, entry in enumerate(entries):
            if not entry or not isinstance(entry, dict):
                continue
            item_url, mtype, ext = extract_url_from_entry(entry)
            if item_url:
                media_items.append({
                    'index': i + 1,
                    'url': item_url,
                    'type': mtype,
                    'ext': ext,
                })
                extracted_url_count += 1

        unique_types = set(m['type'] for m in media_items)
        if len(media_items) == 1:
            if 'video' in unique_types:
                detected_type = 'reel'
            else:
                detected_type = 'single'
        else:
            detected_type = 'carousel'

    else:
        print('NOT a playlist — treating as single entry')
        item_url, mtype, ext = extract_url_from_entry(info)
        if item_url:
            media_items.append({
                'index': 1,
                'url': item_url,
                'type': mtype,
                'ext': ext,
            })
            extracted_url_count += 1
        detected_type = 'reel' if mtype == 'video' else 'single'

    print('MEDIA ITEMS:', len(media_items))
    print('DETECTED TYPE:', detected_type)

    if not media_items:
        return jsonify({
            'success': False,
            'error': 'No downloadable media URLs found.'
        })

    return jsonify({
        'success': True,
        'post_type': detected_type,
        'media_count': len(media_items),
        'items': media_items,
        'title': info.get('title', ''),
        'uploader': info.get('uploader') or info.get('channel', ''),
        'shortcode': info.get('id', ''),
        'ytdl_status': 'ok',
    })


# -----------------------------------------------------------------------
# POST /download-current
# -----------------------------------------------------------------------

@app.route('/download-current', methods=['POST'])
def download_current():
    data = request.get_json(silent=True) or {}
    url = (data.get('url') or '').strip()
    post_type = data.get('post_type', 'single')
    index = data.get('index', 1)

    if not url:
        return jsonify({'success': False, 'error': 'No URL provided.'})

    platform = detect_platform(url)
    ts = timestamp()

    if post_type == 'reel':
        dir_path = VIDEOS_DIR
        base = platform + '_reel_' + ts
    else:
        dir_path = MEDIA_DIR
        base = platform + '_' + ts + '_' + str(index)

    outtmpl = os.path.join(dir_path, base + '.%(ext)s')
    ydl_opts = dict(YTDL_COMMON, outtmpl=outtmpl)

    if post_type == 'carousel' and index:
        ydl_opts['playlist_items'] = str(index)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
    except Exception as e:
        return jsonify({'success': False, 'error': 'Download failed: ' + str(e)})

    pattern = os.path.join(dir_path, base + '.*')
    files = sorted(glob.glob(pattern))

    if not files:
        return jsonify({'success': False, 'error': 'File not found after download.'})

    return jsonify({'success': True, 'files': files, 'count': 1})


# -----------------------------------------------------------------------
# POST /download-all
# -----------------------------------------------------------------------

@app.route('/download-all', methods=['POST'])
def download_all():
    data = request.get_json(silent=True) or {}
    url = (data.get('url') or '').strip()
    post_type = data.get('post_type', 'carousel')

    if not url:
        return jsonify({'success': False, 'error': 'No URL provided.'})

    if post_type not in ('carousel', 'post'):
        return jsonify({
            'success': False,
            'error': 'Download All only applies to carousel posts.'
        })

    platform = detect_platform(url)
    ts = timestamp()
    base = platform + '_' + ts + '_'
    dir_path = MEDIA_DIR
    outtmpl = os.path.join(dir_path, base + '%(playlist_index)s.%(ext)s')

    ydl_opts = dict(YTDL_COMMON, outtmpl=outtmpl)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
    except Exception as e:
        return jsonify({'success': False, 'error': 'Download failed: ' + str(e)})

    pattern = os.path.join(dir_path, base + '*.*')
    files = sorted(glob.glob(pattern))

    return jsonify({'success': True, 'files': files, 'count': len(files)})


# -----------------------------------------------------------------------
# health
# -----------------------------------------------------------------------

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'unidownload-backend',
    })


# -----------------------------------------------------------------------
# main
# -----------------------------------------------------------------------

if __name__ == '__main__':
    print('UniDownload Backend starting on http://127.0.0.1:5000')
    print('  Media:  ' + MEDIA_DIR)
    print('  Videos: ' + VIDEOS_DIR)
    print('  Debug:  ' + DEBUG_DIR)
    print()
    print('Monkey patches applied:')
    print('  _extract_nodes        — image entries now included in carousels')
    print('  _extract_product_media — image URLs from image_versions2')
    print('  _real_extract         — single-image posts handled')
    print()
    print('Currently supported: Instagram')
    print('Extensible to: YouTube, TikTok, X/Twitter, and any yt-dlp source')
    print()
    app.run(host='127.0.0.1', port=5000, debug=False)
