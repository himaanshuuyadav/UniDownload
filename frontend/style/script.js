const BASE_URL = "https://unidownload.up.railway.app";

document.getElementById("fetchBtn").addEventListener("click", fetchQualities);

async function fetchQualities() {
  const url = document.getElementById("urlInput").value.trim();
  const qualitySelect = document.getElementById("qualitySelect");
  const downloadBtn = document.getElementById("downloadBtn");

  qualitySelect.innerHTML = "";
  downloadBtn.disabled = true;

  try {
    const res = await fetch(`${BASE_URL}/get_qualities`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    if (!res.ok) throw new Error(`Server responded with status ${res.status}: ${await res.text()}`);

    const data = await res.json();
    const qualities = data.qualities;
    const video = data.video_info;

    document.getElementById("title").textContent = video.title;
    document.getElementById("thumbnail").src = video.thumbnail;

    qualities.forEach(q => {
      const opt = document.createElement("option");
      opt.value = q.format_id;
      opt.textContent = `${q.resolution} (${Math.round(q.tbr)} kbps)`;
      qualitySelect.appendChild(opt);
    });

    downloadBtn.disabled = false;

  } catch (err) {
    console.error("Error details:", err);
    alert("Failed to fetch video qualities. Check the URL or try again later.");
  }
}

document.getElementById("downloadBtn").addEventListener("click", async () => {
  const url = document.getElementById("urlInput").value.trim();
  const format_id = document.getElementById("qualitySelect").value;

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
