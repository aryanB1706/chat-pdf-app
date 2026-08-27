// Client for the new Python/FastAPI agentic backend.
// Set VITE_AGENTIC_API_URL to enable (e.g. http://localhost:8000/api/v1).
// When unset, callers should fall back to the legacy Node API (VITE_API_URL).

export const AGENTIC_BASE = (
  import.meta.env.VITE_AGENTIC_API_URL || ""
).replace(/\/$/, "");

export const isAgenticEnabled = () => Boolean(AGENTIC_BASE);

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
