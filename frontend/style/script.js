const BASE_URL = "https://unidownload.up.railway.app";

document.getElementById("fetch-qualities").addEventListener("click", fetchQualities);

async function fetchQualities() {
  const url = document.getElementById("video-url").value.trim();
  const qualityContainer = document.getElementById("quality-options");
  const selectedQuality = document.getElementById("selected-quality");
  const downloadBtn = document.getElementById("download-btn");
  const videoInfo = document.getElementById("video-info");
  const loadingContainer = document.querySelector(".loading-container");

  qualityContainer.innerHTML = "";
  selectedQuality.textContent = "Select Quality";
  downloadBtn.style.display = "none";
  videoInfo.style.display = "none";
  loadingContainer.style.display = "block";

  try {
    const res = await fetch(`${BASE_URL}/get_qualities`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    loadingContainer.style.display = "none";

    if (!res.ok) throw new Error(`Server responded with status ${res.status}: ${await res.text()}`);

    const data = await res.json();
    const qualities = data.qualities;
    const video = data.video_info;

    document.getElementById("video-title").textContent = video.title;
    document.getElementById("video-thumbnail").src = video.thumbnail;
    videoInfo.style.display = "block";

    qualities.forEach(q => {
      const item = document.createElement("div");
      item.className = "select-item";
      item.textContent = `${q.resolution} (${Math.round(q.tbr)} kbps)`;
      item.dataset.formatId = q.format_id;
      item.addEventListener("click", () => {
        selectedQuality.textContent = item.textContent;
        selectedQuality.dataset.formatId = q.format_id;
        qualityContainer.style.display = "none";
        downloadBtn.style.display = "inline-block";
      });
      qualityContainer.appendChild(item);
    });

    selectedQuality.addEventListener("click", () => {
      qualityContainer.style.display = qualityContainer.style.display === "block" ? "none" : "block";
    });

  } catch (err) {
    loadingContainer.style.display = "none";
    console.error("Error details:", err);
    alert("Failed to fetch video qualities. Check the URL or try again later.");
  }
}

document.getElementById("download-btn").addEventListener("click", async () => {
  const url = document.getElementById("video-url").value.trim();
  const format_id = document.getElementById("selected-quality").dataset.formatId;

  try {
    const res = await fetch(`${BASE_URL}/download`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, format_id }),
    });

    if (!res.ok) throw new Error(`Download error: ${res.status}`);

    const data = await res.json();
    const downloadUrl = data.download_url;

    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = "";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

  } catch (err) {
    console.error("Download error:", err);
    alert("Failed to start download. Please try again.");
  }
});
