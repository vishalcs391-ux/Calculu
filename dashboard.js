import { requireAuth, wireLogout } from "./auth.js";
import { apiGet } from "./api.js";

requireAuth(async () => {
  wireLogout();
  await loadProgress();
  await loadPlanner();
});

async function loadProgress() {
  const el = document.getElementById("progress-summary");
  try {
    const data = await apiGet("/progress?days=30");
    el.innerHTML = `
      <div class="grid">
        <div class="card"><div class="stat-value">${data.current_streak}</div><div class="muted">Day streak</div></div>
        <div class="card"><div class="stat-value">${data.total_study_minutes}</div><div class="muted">Minutes studied</div></div>
        <div class="card"><div class="stat-value">${data.quizzes_taken}</div><div class="muted">Quizzes taken</div></div>
        <div class="card"><div class="stat-value">${data.avg_quiz_score ?? "-"}</div><div class="muted">Avg quiz score %</div></div>
      </div>`;
  } catch (e) {
    el.innerHTML = `<div class="error-box">Could not load progress: ${e.message}</div>`;
  }
}

async function loadPlanner() {
  const el = document.getElementById("planner-list");
  try {
    const sessions = await apiGet("/study/planner");
    if (!sessions.length) {
      el.innerHTML = `<p class="muted">No study plan yet. <a href="planner.html">Create one</a>.</p>`;
      return;
    }
    el.innerHTML = sessions.slice(0, 5).map((s) => `
      <div class="card" style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <strong>${s.topic}</strong><br/>
          <span class="muted">${new Date(s.scheduled_at).toLocaleDateString()} · ${s.duration_minutes} min</span>
        </div>
        <span class="muted">${s.status}</span>
      </div>`).join("");
  } catch (e) {
    el.innerHTML = `<div class="error-box">Could not load planner: ${e.message}</div>`;
  }
}
