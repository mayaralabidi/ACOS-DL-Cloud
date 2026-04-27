import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 300_000,
});

export async function processVideo(file, onUploadProgress) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/sessions/process", form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });
  return data;
}

export async function getSession(sessionId) {
  const { data } = await api.get(`/sessions/${sessionId}`);
  return data;
}

export async function listSessions(skip = 0, limit = 20) {
  const { data } = await api.get("/sessions/", { params: { skip, limit } });
  return data;
}

export async function overrideItem(sessionId, action, label, qty = 1) {
  const { data } = await api.patch(`/sessions/${sessionId}/override`, {
    action,
    label,
    qty,
  });
  return data;
}

export async function confirmSession(sessionId) {
  const { data } = await api.post(`/sessions/${sessionId}/confirm`);
  return data;
}

export async function cancelSession(sessionId) {
  await api.delete(`/sessions/${sessionId}`);
}

export async function listProducts() {
  const { data } = await api.get("/products/");
  return data;
}
