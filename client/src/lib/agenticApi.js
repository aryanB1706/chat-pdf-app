// Client for the Python/FastAPI agentic backend (the only backend).
// VITE_AGENTIC_API_URL e.g. http://localhost:8000/api/v1 (dev default below).

export const AGENTIC_BASE = (
  import.meta.env.VITE_AGENTIC_API_URL || "http://localhost:8000/api/v1"
).replace(/\/$/, "");

async function req(path, opts = {}) {
  const res = await fetch(`${AGENTIC_BASE}${path}`, opts);
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Agentic API ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

export const uploadDocument = async (file) => {
  const form = new FormData();
  form.append("file", file);
  return req("/documents/upload", { method: "POST", body: form });
};

export const getDocStatus = (documentId) =>
  req(`/documents/${documentId}/status`);

export const waitForReady = async (
  documentId,
  { timeoutMs = 10 * 60 * 1000, intervalMs = 3000 } = {}
) => {
  const start = Date.now();
  for (;;) {
    const s = await getDocStatus(documentId);
    if (s.status === "ready" || s.status === "failed") return s;
    if (Date.now() - start > timeoutMs) throw new Error("Ingestion timed out");
    await new Promise((r) => setTimeout(r, intervalMs));
  }
};

export const askQuestion = (documentId, question, top_k = 5) =>
  req("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, question, top_k }),
  });

export const getStats = () => req("/stats");

export const generateQuiz = (documentId, num_questions = 5) =>
  req("/quiz", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, num_questions }),
  });

export const generateMindMap = (documentId) =>
  req("/mindmap", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId }),
  });

export const generatePodcast = (documentId, language = "english") =>
  req("/podcast", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, language }),
  });

export const analyzeCrop = (image, question) =>
  req("/analyze-crop", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image, question: question || "Explain this image." }),
  });
