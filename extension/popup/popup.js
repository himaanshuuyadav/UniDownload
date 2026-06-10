/* ========================================================================
   UniDownload — popup controller
   Communicates with the local Flask backend at http://127.0.0.1:5000
   ======================================================================== */

var BACKEND = 'http://127.0.0.1:5000';

var currentUrl = '';
var currentPostType = '';
var currentMediaCount = 0;
var currentItems = [];

document.addEventListener('DOMContentLoaded', async function () {
  var tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  var tab = tabs[0];

  if (!tab || !tab.url) {
    showMessage('Could not determine the current tab URL.', 'error');
    return;
  }

  currentUrl = tab.url;
  document.getElementById('currentUrl').textContent = currentUrl;

  if (currentUrl.indexOf('instagram.com') === -1 ||
      (currentUrl.indexOf('/p/') === -1 && currentUrl.indexOf('/reel/') === -1)) {
    showMessage('Open a supported post or reel.', 'error');
    document.getElementById('statusText').textContent = 'Not supported';
    document.getElementById('btnAnalyze').disabled = true;
    return;
  }

  document.getElementById('statusText').textContent = 'Ready to analyze';

  /* ---------- events ---------- */

  document.getElementById('btnAnalyze').addEventListener('click', handleAnalyze);
  document.getElementById('btnDownloadCurrent').addEventListener('click', handleDownloadCurrent);
  document.getElementById('btnDownloadAll').addEventListener('click', handleDownloadAll);

  document.getElementById('debugToggle').addEventListener('click', function () {
    var body = document.getElementById('debugBody');
    var toggle = document.getElementById('debugToggle');
    var hidden = body.classList.contains('hidden');
    body.classList.toggle('hidden');
    toggle.textContent = hidden ? 'Debug Info ▾' : 'Debug Info ▸';
  });
});

/* ========================================================================
   Analyze
   ======================================================================== */

async function handleAnalyze() {
  setAnalyzing(true);
  hideMessage();

  try {
    var resp = await fetch(BACKEND + '/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: currentUrl }),
    });

    if (!resp.ok) {
      showMessage('Backend returned HTTP ' + resp.status, 'error');
      setAnalyzing(false);
      return;
    }

    var data = await resp.json();
    setAnalyzing(false);

    if (!data.success) {
      showMessage(data.error || 'Analysis failed.', 'error');
      document.getElementById('debugBackend').textContent = 'error';
      return;
    }

    currentPostType = data.post_type;
    currentMediaCount = data.media_count;
    currentItems = data.items || [];

    showResult(data);
    showDebug(data);
    showMessage('Analysis complete.', 'success', 2000);

  } catch (err) {
    setAnalyzing(false);
    showMessage('Local downloader service not running. Start the backend with: python server.py', 'error');
    document.getElementById('debugBackend').textContent = 'unreachable';
  }
}

function setAnalyzing(active) {
  var btn = document.getElementById('btnAnalyze');
  btn.disabled = active;
  btn.textContent = active ? 'Analyzing...' : 'Analyze';
  document.getElementById('statusText').textContent = active ? 'Analyzing...' : 'Ready';
}

/* ========================================================================
   Download Current
   ======================================================================== */

async function handleDownloadCurrent() {
  if (!currentUrl || currentMediaCount === 0) return;

  hideMessage();

  var index = 1;
  var ext = getFileExtension(currentItems, index);

  try {
    var resp = await fetch(BACKEND + '/download-current', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: currentUrl,
        post_type: currentPostType,
        index: index,
      }),
    });

    var data = await resp.json();

    if (data.success && data.files && data.files.length > 0) {
      showMessage('Downloaded: ' + data.files[0], 'success');
    } else {
      showMessage(data.error || 'Download failed.', 'error');
    }
  } catch (err) {
    showMessage('Backend unreachable. Is the server running?', 'error');
  }
}

/* ========================================================================
   Download All
   ======================================================================== */

async function handleDownloadAll() {
  if (!currentUrl || currentMediaCount < 2) return;

  hideMessage();

  try {
    var resp = await fetch(BACKEND + '/download-all', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: currentUrl,
        post_type: currentPostType,
      }),
    });

    var data = await resp.json();

    if (data.success && data.files) {
      showMessage('Downloaded ' + data.count + ' file' + (data.count !== 1 ? 's' : '') + '.', 'success');
    } else {
      showMessage(data.error || 'Download failed.', 'error');
    }
  } catch (err) {
    showMessage('Backend unreachable. Is the server running?', 'error');
  }
}

/* ========================================================================
   UI helpers
   ======================================================================== */

function showResult(data) {
  document.getElementById('resultPanel').classList.remove('hidden');

  document.getElementById('platformName').textContent = 'Instagram';

  var typeMap = { single: 'Single Image', carousel: 'Carousel', reel: 'Video Reel' };
  document.getElementById('postType').textContent = typeMap[data.post_type] || data.post_type;
  document.getElementById('mediaCount').textContent = data.media_count;

  document.getElementById('btnDownloadCurrent').disabled = false;

  var btnAll = document.getElementById('btnDownloadAll');
  var hasMultiple = data.post_type === 'carousel' && data.media_count > 1;
  btnAll.disabled = !hasMultiple;

  document.getElementById('statusText').textContent = 'Ready';
}

function showDebug(data) {
  document.getElementById('debug').classList.remove('hidden');
  document.getElementById('debugBackend').textContent = 'connected';
  document.getElementById('debugYtdl').textContent = data.ytdl_status || 'ok';
  document.getElementById('debugUrlCount').textContent = (data.items || []).length;

  var list = document.getElementById('debugUrlList');
  if (data.items && data.items.length > 0) {
    list.innerHTML = data.items.map(function (item) {
      return '<div>[' + item.index + '] ' + item.type + ' — ' + item.url.substring(0, 50) + '…</div>';
    }).join('');
    list.classList.remove('hidden');
  } else {
    list.classList.add('hidden');
  }
}

function showMessage(text, type, autoHideMs) {
  var el = document.getElementById('message');
  el.textContent = text;
  el.className = 'message';
  el.classList.add('message-' + (type || 'error'));
  el.classList.remove('hidden');

  if (autoHideMs) {
    setTimeout(function () { el.classList.add('hidden'); }, autoHideMs);
  }
}

function hideMessage() {
  document.getElementById('message').classList.add('hidden');
}

function getFileExtension(items, index) {
  if (!items || !items.length) return 'jpg';
  var found = null;
  for (var i = 0; i < items.length; i++) {
    if (items[i].index === index) { found = items[i]; break; }
  }
  if (!found) found = items[0];
  return found.ext || 'jpg';
}
