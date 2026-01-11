// API Base URL - use relative path for production
const API_BASE = '/api';

// Global state
let currentMediaData = null;
let currentUrl = '';

// DOM Elements
const urlInput = document.getElementById('urlInput');
const detectBtn = document.getElementById('detectBtn');
const statusMessage = document.getElementById('statusMessage');
const mediaInfo = document.getElementById('mediaInfo');
const downloadProgress = document.getElementById('downloadProgress');
const downloadsList = document.getElementById('downloadsList');

// Event Listeners
detectBtn.addEventListener('click', handleDetect);
urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleDetect();
});

// Handle Detect Button
async function handleDetect() {
    const url = urlInput.value.trim();
    
    if (!url) {
        showStatus('Please enter a URL', 'error');
        return;
    }

    currentUrl = url;
    setLoading(true);
    hideStatus();
    hideMediaInfo();

    try {
        const response = await fetch(`${API_BASE}/detect`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to detect platform');
        }

        currentMediaData = data;
        displayMediaInfo(data);
        showStatus('Media information loaded successfully!', 'success');

    } catch (error) {
        showStatus(error.message, 'error');
    } finally {
        setLoading(false);
    }
}

// Display Media Info
function displayMediaInfo(data) {
    // Set thumbnail
    const thumbnail = document.getElementById('thumbnail');
    thumbnail.src = data.thumbnail || 'https://via.placeholder.com/200x112?text=No+Thumbnail';

    // Set platform badge
    const platformBadge = document.getElementById('platformBadge');
    platformBadge.textContent = data.platform;
    platformBadge.className = `platform-badge ${data.platform}`;

    // Set title and details
    document.getElementById('title').textContent = data.title;
    document.getElementById('uploader').textContent = `👤 ${data.uploader}`;
    
    const durationEl = document.getElementById('duration');
    if (data.duration) {
        const minutes = Math.floor(data.duration / 60);
        const seconds = data.duration % 60;
        durationEl.textContent = `⏱️ ${minutes}:${seconds.toString().padStart(2, '0')}`;
        durationEl.style.display = 'block';
    } else {
        durationEl.style.display = 'none';
    }

    // Hide all option sections first
    document.getElementById('youtubeOptions').classList.add('hidden');
    document.getElementById('instagramOptions').classList.add('hidden');
    document.getElementById('facebookOptions').classList.add('hidden');

    // Show platform-specific options
    if (data.platform === 'youtube') {
        displayYouTubeOptions(data);
    } else if (data.platform === 'instagram') {
        displayInstagramOptions(data);
    } else if (data.platform === 'facebook') {
        displayFacebookOptions(data);
    }

    mediaInfo.classList.remove('hidden');
}

// Display YouTube Options
function displayYouTubeOptions(data) {
    const optionsSection = document.getElementById('youtubeOptions');
    const formatsList = document.getElementById('formatsList');
    
    // Clear previous formats
    formatsList.innerHTML = '';

    // Add format buttons
    if (data.formats && data.formats.length > 0) {
        data.formats.forEach(format => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.textContent = `📹 ${format.label}`;
            btn.dataset.option = 'video';
            btn.dataset.formatId = format.format_id;
            btn.onclick = () => handleDownload('youtube', 'video', format.format_id);
            formatsList.appendChild(btn);
        });
    }

    // Show/hide subtitle button
    const subtitlesBtn = document.getElementById('subtitlesBtn');
    if (data.has_subtitles) {
        subtitlesBtn.style.display = 'block';
    } else {
        subtitlesBtn.style.display = 'none';
    }

    // Show/hide playlist button based on URL
    const playlistBtn = document.getElementById('playlistBtn');
    if (currentUrl.includes('playlist') || currentUrl.includes('list=')) {
        playlistBtn.style.display = 'block';
    } else {
        playlistBtn.style.display = 'none';
    }

    // Add click handlers for other options
    optionsSection.querySelectorAll('.option-btn[data-option]').forEach(btn => {
        if (!btn.dataset.formatId) {
            btn.onclick = () => handleDownload('youtube', btn.dataset.option);
        }
    });

    optionsSection.classList.remove('hidden');
}

// Display Instagram Options
function displayInstagramOptions(data) {
    const optionsSection = document.getElementById('instagramOptions');
    
    // Add click handlers
    optionsSection.querySelectorAll('.option-btn').forEach(btn => {
        btn.onclick = () => handleDownload('instagram', btn.dataset.option);
    });

    optionsSection.classList.remove('hidden');
}

// Display Facebook Options
function displayFacebookOptions(data) {
    const optionsSection = document.getElementById('facebookOptions');
    
    // Add click handlers
    optionsSection.querySelectorAll('.option-btn').forEach(btn => {
        btn.onclick = () => handleDownload('facebook', btn.dataset.option);
    });

    optionsSection.classList.remove('hidden');
}

// Handle Download
async function handleDownload(platform, option, formatId = null) {
    const downloadData = {
        url: currentUrl,
        platform: platform,
        option: option
    };

    if (formatId) {
        downloadData.format_id = formatId;
    }

    // Add to downloads list
    const downloadId = Date.now();
    addDownloadItem(downloadId, option, 'Downloading...');

    try {
        const response = await fetch(`${API_BASE}/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(downloadData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Download failed');
        }

        updateDownloadItem(downloadId, 'success', data.message, data.files);
        showStatus(data.message, 'success');

    } catch (error) {
        updateDownloadItem(downloadId, 'error', error.message);
        showStatus(error.message, 'error');
    }
}

// Add Download Item
function addDownloadItem(id, option, message) {
    downloadProgress.classList.remove('hidden');
    
    const item = document.createElement('div');
    item.className = 'download-item';
    item.id = `download-${id}`;
    item.innerHTML = `
        <div class="status">⏳</div>
        <div class="details">
            <div class="name">${option.toUpperCase()}</div>
            <div class="message">${message}</div>
        </div>
    `;
    
    downloadsList.insertBefore(item, downloadsList.firstChild);
}

// Update Download Item
function updateDownloadItem(id, status, message, files = []) {
    const item = document.getElementById(`download-${id}`);
    if (!item) return;

    const statusIcon = item.querySelector('.status');
    const messageEl = item.querySelector('.message');

    if (status === 'success') {
        statusIcon.textContent = '✅';
        messageEl.textContent = message;
        
        // Add download links if files are available
        if (files && files.length > 0) {
            const linksContainer = document.createElement('div');
            linksContainer.style.marginTop = '8px';
            
            files.forEach(file => {
                const link = document.createElement('a');
                link.href = file.url;
                link.textContent = `📥 Download ${file.filename}`;
                link.className = 'download-link';
                link.style.display = 'block';
                link.style.color = '#4ade80';
                link.style.textDecoration = 'none';
                link.style.marginTop = '4px';
                link.style.fontSize = '0.9em';
                link.download = file.filename;
                linksContainer.appendChild(link);
            });
            
            item.querySelector('.details').appendChild(linksContainer);
        }
    } else if (status === 'error') {
        statusIcon.textContent = '❌';
        messageEl.textContent = message;
    }
}

// Show Status Message
function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.classList.remove('hidden');
}

// Hide Status Message
function hideStatus() {
    statusMessage.classList.add('hidden');
}

// Hide Media Info
function hideMediaInfo() {
    mediaInfo.classList.add('hidden');
}

// Set Loading State
function setLoading(loading) {
    if (loading) {
        detectBtn.classList.add('loading');
        detectBtn.disabled = true;
    } else {
        detectBtn.classList.remove('loading');
        detectBtn.disabled = false;
    }
}

// Check API Health on Load
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        console.log('API Status:', data);
    } catch (error) {
        showStatus('⚠️ API server is not running. Please start the server first.', 'error');
    }
});
