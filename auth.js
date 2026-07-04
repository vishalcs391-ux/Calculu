// Handles sign up / sign in / sign out and redirects.
import { auth } from "./firebase-config.js";
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
} from "https://www.gstatic.com/firebasejs/10.13.0/firebase-auth.js";

export function initAuthForm() {
  const form = document.getElementById("auth-form");
  const errorBox = document.getElementById("auth-error");
  const toggleBtn = document.getElementById("toggle-mode");
  let mode = "signin"; // or "signup"

  toggleBtn.addEventListener("click", () => {
    mode = mode === "signin" ? "signup" : "signin";
    document.getElementById("submit-btn").textContent = mode === "signin" ? "Sign In" : "Sign Up";
    toggleBtn.textContent = mode === "signin" ? "Need an account? Sign up" : "Have an account? Sign in";
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBox.style.display = "none";
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    try {
      if (mode === "signin") {
        await signInWithEmailAndPassword(auth, email, password);
      } else {
        await createUserWithEmailAndPassword(auth, email, password);
      }
      window.location.href = "dashboard.html";
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.style.display = "block";
    }
  });
}

export function requireAuth(onReady) {
  onAuthStateChanged(auth, (user) => {
    if (!user) {
      window.location.href = "index.html";
    } else {
      onReady(user);
    }
  });
}

export function wireLogout(buttonId = "logout-btn") {
  const btn = document.getElementById(buttonId);
  if (btn) btn.addEventListener("click", () => signOut(auth).then(() => (window.location.href = "index.html")));
}
