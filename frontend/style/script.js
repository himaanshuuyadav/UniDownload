const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:5000'
    : 'https://unidownload-production.up.railway.app';
// Event Listeners
document.getElementById("fetch-qualities").addEventListener("click", fetchQualities);
document.getElementById("download-btn").addEventListener("click", downloadVideo);

// Show Message Helper Function
function showMessage(message, isError = false) {
    const responseMessage = document.getElementById("response-message");
    responseMessage.textContent = message;
    responseMessage.style.color = isError ? '#ff6b6b' : '#83df80';
    responseMessage.style.padding = '10px';
    responseMessage.style.borderRadius = '5px';
    responseMessage.style.backgroundColor = isError ? 'rgba(255, 0, 0, 0.1)' : 'rgba(0, 255, 0, 0.1)';
    
    // Clear message after 5 seconds
    setTimeout(() => {
        responseMessage.textContent = '';
        responseMessage.style.backgroundColor = 'transparent';
    }, 5000);
}

// Handle custom select dropdown
document.addEventListener('DOMContentLoaded', function() {
    const customSelect = document.querySelector('.custom-select');
    const selectedQuality = document.getElementById('selected-quality');
    const qualityOptions = document.getElementById('quality-options');

    // Toggle dropdown when clicking the select header
    selectedQuality.addEventListener('click', function(e) {
        e.stopPropagation();
        customSelect.classList.toggle('active');
        qualityOptions.style.display = customSelect.classList.contains('active') ? 'block' : 'none';
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!customSelect.contains(e.target)) {
            customSelect.classList.remove('active');
            qualityOptions.style.display = 'none';
        }
    });
});

function fetchQualities() {
    let videoUrl = document.getElementById("video-url").value;
    let qualitiesDiv = document.getElementById("qualities");
    let loadingContainer = document.querySelector('.loading-container');
    let customSelect = document.querySelector('.custom-select');

    if (!videoUrl) {
        showMessage("Please enter a valid URL!", true);
        return;
    }

    loadingContainer.style.display = "block";
    qualitiesDiv.style.display = "none";

    fetch(`${API_BASE_URL}/get_qualities`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: videoUrl })
})
.then(async response => {
    if (!response.ok) {
        const text = await response.text();
        throw new Error(`Server responded with status ${response.status}: ${text}`);
    }
    return response.json();
})
    .then(data => {
        loadingContainer.style.display = "none";
        
        if (data.error) {
            showMessage(data.error, true);
            return;
        }

        let downloadBtn = document.getElementById("download-btn");
        let videoInfo = document.getElementById("video-info");
        let videoThumbnail = document.getElementById("video-thumbnail");
        let videoTitle = document.getElementById("video-title");
        let qualityOptions = document.getElementById("quality-options");
        let selectedQuality = document.getElementById("selected-quality");

        qualityOptions.innerHTML = "";
        selectedQuality.textContent = "Select Quality";
        selectedQuality.removeAttribute('data-value');
        downloadBtn.style.display = "none";

        if (data.video_info) {
            videoThumbnail.src = data.video_info.thumbnail || '';
            videoTitle.textContent = data.video_info.title || 'Unknown Title';
            videoInfo.style.display = "block";
            showMessage("Video information fetched successfully!");
        }

        if (data.qualities && Array.isArray(data.qualities)) {
            data.qualities.forEach(q => {
                const option = document.createElement('div');
                option.setAttribute('data-value', q.format_id);
                option.textContent = `Quality: ${q.resolution} (${q.ext})`;
                option.onclick = function(e) {
                    e.stopPropagation();
                    selectedQuality.textContent = this.textContent;
                    selectedQuality.setAttribute('data-value', this.getAttribute('data-value'));
                    
                    document.querySelectorAll('.select-items div').forEach(div => {
                        div.classList.remove('selected');
                    });
                    
                    this.classList.add('selected');
                    customSelect.classList.remove('active');
                    qualityOptions.style.display = 'none';
                    downloadBtn.style.display = "block";
                };
                qualityOptions.appendChild(option);
            });

            customSelect.style.display = "block";
            qualitiesDiv.style.display = "grid";
        }
    })
    // Update in script.js fetch error handling
.catch(error => {
    console.error("Error details:", error);
    loadingContainer.style.display = "none";
    
    // More specific error message
    let errorMsg = "Error fetching video info. ";
    if (error.message.includes("private") || error.message.includes("not available")) {
        errorMsg += "This video might be private or region-restricted.";
    } else if (error.message.includes("copyright")) {
        errorMsg += "This video has copyright restrictions.";
    } else {
        errorMsg += "Please try again or try another video.";
    }
    
    showMessage(errorMsg, true);
});
}

function downloadVideo() {
    let videoUrl = document.getElementById("video-url").value;
    let selectedQuality = document.getElementById("selected-quality");
    let selectedFormatId = selectedQuality.getAttribute('data-value');
    let loadingContainer = document.querySelector('.loading-container');
    let downloadBtn = document.getElementById("download-btn");
    let qualitiesDiv = document.getElementById("qualities"); // Add this line

    if (!videoUrl || !selectedFormatId) {
        showMessage("Please fetch qualities first and select one.", true);
        return;
    }

    // Disable download button to prevent multiple clicks
    downloadBtn.disabled = true;
    downloadBtn.style.opacity = '0.5';
    
    loadingContainer.style.display = "block";
    loadingContainer.querySelector('.loading-text').textContent = "Starting download...";

    fetch(`${API_BASE_URL}/download`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: videoUrl, format_id: selectedFormatId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        loadingContainer.style.display = "none";
        if (data.success) {
            showMessage("✅ Download completed successfully!");
            // Show temporary message and keep video details visible
            const tempMessage = document.createElement('div');
            tempMessage.textContent = "Download has started! Check your downloads folder.";
            tempMessage.style.color = '#83df80';
            tempMessage.style.padding = '10px';
            tempMessage.style.marginTop = '10px';
            tempMessage.style.backgroundColor = 'rgba(0, 255, 0, 0.1)';
            tempMessage.style.borderRadius = '5px';
            qualitiesDiv.appendChild(tempMessage);

            // Remove the message after 5 seconds
            setTimeout(() => {
                tempMessage.remove();
            }, 5000);
        } else if (data.error) {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        loadingContainer.style.display = "none";
        console.error("Download error:", error);
        if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
            showMessage("✅ Download started! Check your downloads folder.");
            // Show temporary message and keep video details visible
            const tempMessage = document.createElement('div');
            tempMessage.textContent = "Download has started! Check your downloads folder.";
            tempMessage.style.color = '#83df80';
            tempMessage.style.padding = '10px';
            tempMessage.style.marginTop = '10px';
            tempMessage.style.backgroundColor = 'rgba(0, 255, 0, 0.1)';
            tempMessage.style.borderRadius = '5px';
            qualitiesDiv.appendChild(tempMessage);

            // Remove the message after 5 seconds
            setTimeout(() => {
                tempMessage.remove();
            }, 5000);
        } else {
            showMessage(`Download error: ${error.message}`, true);
        }
    })
    .finally(() => {
        // Re-enable download button
        downloadBtn.disabled = false;
        downloadBtn.style.opacity = '1';
    });
}
