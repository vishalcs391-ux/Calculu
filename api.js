// Small fetch wrapper: attaches the Firebase ID token to every request
// and centralizes error handling / loading states for the whole frontend.
import { auth } from "./firebase-config.js";

const API_BASE = "http://localhost:8000/api/v1"; // change to your deployed backend URL in production

async function authHeader() {
  const user = auth.currentUser;
  if (!user) throw new Error("Not signed in");
  const token = await user.getIdToken();
  return { Authorization: `Bearer ${token}` };
}

export async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`, { headers: await authHeader() });
  return handle(res);
}

export async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(await authHeader()) },
    body: body ? JSON.stringify(body) : undefined,
  });
  return handle(res);
}

export async function apiPatch(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...(await authHeader()) },
    body: body ? JSON.stringify(body) : undefined,
  });
  return handle(res);
}

export async function apiUpload(path, formData) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: await authHeader(), // do NOT set Content-Type; browser sets multipart boundary
    body: formData,
  });
  return handle(res);
}

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch (_) {}
    throw new Error(detail);
  }
  return res.status === 204 ? null : res.json();
}
