import { requireAuth, wireLogout } from "./auth.js";
import { apiPost } from "./api.js";

const params = new URLSearchParams(window.location.search);
const summaryId = params.get("summary_id");
let quiz = null;
const selected = [];

requireAuth(async () => {
  wireLogout();
  if (!summaryId) {
    document.getElementById("quiz-area").innerHTML = `<p class="muted">No summary selected. Go to <a href="upload.html">Upload</a> first.</p>`;
    return;
  }
  await generateQuiz();
});

async function generateQuiz() {
  const area = document.getElementById("quiz-area");
  area.innerHTML = `<p class="loading">Generating quiz with AI...</p>`;
  try {
    quiz = await apiPost(`/content/summaries/${summaryId}/quiz?num_questions=10&difficulty=medium`);
    renderQuiz();
  } catch (e) {
    area.innerHTML = `<div class="error-box">${e.message}</div>`;
  }
}

function renderQuiz() {
  const area = document.getElementById("quiz-area");
  area.innerHTML = quiz.questions.map((q, qi) => `
    <div class="card">
      <p><strong>${qi + 1}. ${q.question}</strong></p>
      ${q.options.map((opt, oi) => `
        <div class="quiz-option" data-q="${qi}" data-o="${oi}">${opt}</div>
      `).join("")}
    </div>
  `).join("") + `<button class="btn" id="submit-quiz">Submit Quiz</button>`;

  area.querySelectorAll(".quiz-option").forEach((el) => {
    el.addEventListener("click", () => {
      const q = +el.dataset.q, o = +el.dataset.o;
      area.querySelectorAll(`.quiz-option[data-q="${q}"]`).forEach((e2) => e2.classList.remove("selected"));
      el.classList.add("selected");
      selected[q] = o;
    });
  });

  document.getElementById("submit-quiz").addEventListener("click", submitQuiz);
}

async function submitQuiz() {
  try {
    const result = await apiPost(`/content/quizzes/${quiz.id}/submit`, { answers: selected });
    document.getElementById("quiz-result").innerHTML = `
      <div class="card"><h2>Score: ${result.score}%</h2></div>`;
    result.questions.forEach((q, qi) => {
      document.querySelectorAll(`.quiz-option[data-q="${qi}"]`).forEach((el) => {
        const oi = +el.dataset.o;
        if (oi === q.correct_index) el.classList.add("correct");
        else if (selected[qi] === oi) el.classList.add("incorrect");
      });
    });
  } catch (e) {
    document.getElementById("quiz-result").innerHTML = `<div class="error-box">${e.message}</div>`;
  }
}
