import { requireAuth, wireLogout } from "./auth.js";
import { apiPost } from "./api.js";

requireAuth(() => {
  wireLogout();
  const form = document.getElementById("chat-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if (!message) return;
    addMessage(message, "user");
    input.value = "";
    addMessage("Thinking...", "tutor", "thinking");
    try {
      const res = await apiPost("/study/tutor/chat", { message });
      replaceThinking(res.reply);
    } catch (err) {
      replaceThinking(`Error: ${err.message}`);
    }
  });
});

function addMessage(text, role, id) {
  const win = document.getElementById("chat-window");
  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  div.textContent = text;
  if (id) div.id = id;
  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
}

function replaceThinking(text) {
  const el = document.getElementById("thinking");
  if (el) { el.textContent = text; el.removeAttribute("id"); }
}
