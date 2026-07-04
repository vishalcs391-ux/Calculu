import { requireAuth, wireLogout } from "./auth.js";
import { apiPost, apiUpload, apiGet } from "./api.js";

requireAuth(async () => {
  wireLogout();
  wirePdfUpload();
  wireYoutubeUpload();
  await loadSources();
});

function wirePdfUpload() {
  const form = document.getElementById("pdf-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("pdf-file");
    if (!fileInput.files.length) return;
    setStatus("Uploading and extracting text...");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    try {
      const source = await apiUpload("/sources/pdf", formData);
      setStatus(`Uploaded: ${source.title} (status: ${source.status})`);
      await generateNotes(source.id);
    } catch (err) {
      setStatus(`Error: ${err.message}`, true);
    }
  });
}

function wireYoutubeUpload() {
  const form = document.getElementById("youtube-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = document.getElementById("youtube-url").value;
    setStatus("Fetching transcript...");
    try {
      const source = await apiPost("/sources/youtube", { youtube_url: url });
      setStatus(`Added: ${source.title} (status: ${source.status})`);
      await generateNotes(source.id);
    } catch (err) {
      setStatus(`Error: ${err.message}`, true);
    }
  });
}

async function generateNotes(sourceId) {
  setStatus("Generating notes with AI... this can take a moment.");
  try {
    const summary = await apiPost(`/content/sources/${sourceId}/summarize`);
    setStatus("Notes ready!");
    window.location.href = `flashcards.html?summary_id=${summary.id}`;
  } catch (err) {
    setStatus(`Error generating notes: ${err.message}`, true);
  }
}

function setStatus(text, isError = false) {
  const el = document.getElementById("upload-status");
  el.textContent = text;
  el.className = isError ? "error-box" : "loading";
  el.style.display = "block";
}

async function loadSources() {
  const el = document.getElementById("source-list");
  try {
    const sources = await apiGet("/sources");
    el.innerHTML = sources.map((s) => `
      <div class="card">
        <strong>${s.title || s.source_type}</strong> — <span class="muted">${s.status}</span>
      </div>`).join("") || `<p class="muted">No sources yet.</p>`;
  } catch (e) {
    el.innerHTML = `<div class="error-box">${e.message}</div>`;
  }
}
