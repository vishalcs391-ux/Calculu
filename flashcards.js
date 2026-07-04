import { requireAuth, wireLogout } from "./auth.js";
import { apiGet, apiPost } from "./api.js";

const params = new URLSearchParams(window.location.search);
const summaryId = params.get("summary_id");
let cards = [];
let index = 0;

requireAuth(async () => {
  wireLogout();
  if (!summaryId) {
    document.getElementById("flashcard-area").innerHTML = `<p class="muted">No summary selected. Go to <a href="upload.html">Upload</a> first.</p>`;
    return;
  }
  await loadOrGenerate();
});

async function loadOrGenerate() {
  const area = document.getElementById("flashcard-area");
  area.innerHTML = `<p class="loading">Loading flashcards...</p>`;
  try {
    let list = await apiGet(`/content/summaries/${summaryId}/flashcards`);
    if (!list.length) {
      list = await apiPost(`/content/summaries/${summaryId}/flashcards?count=12`);
    }
    cards = list;
    index = 0;
    renderCard();
  } catch (e) {
    area.innerHTML = `<div class="error-box">${e.message}</div>`;
  }
}

function renderCard() {
  const area = document.getElementById("flashcard-area");
  if (!cards.length) {
    area.innerHTML = `<p class="muted">No flashcards yet.</p>`;
    return;
  }
  const card = cards[index];
  area.innerHTML = `
    <p class="muted">Card ${index + 1} of ${cards.length} · ${card.difficulty}</p>
    <div class="flashcard" id="card">
      <div class="flashcard-inner">
        <div class="flashcard-face front">${card.question}</div>
        <div class="flashcard-face back">${card.answer}</div>
      </div>
    </div>
    <div style="margin-top:16px; display:flex; gap:10px; justify-content:center;">
      <button class="btn secondary" id="btn-incorrect">Got it wrong</button>
      <button class="btn" id="btn-correct">Got it right</button>
    </div>`;

  document.getElementById("card").addEventListener("click", (e) => {
    e.currentTarget.classList.toggle("flipped");
  });
  document.getElementById("btn-correct").addEventListener("click", () => mark("correct"));
  document.getElementById("btn-incorrect").addEventListener("click", () => mark("incorrect"));
}

async function mark(result) {
  const card = cards[index];
  try {
    await apiPost(`/content/flashcards/${card.id}/review`, { result });
  } catch (_) { /* non-blocking */ }
  index = (index + 1) % cards.length;
  renderCard();
}
