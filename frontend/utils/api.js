const API = process.env.NEXT_PUBLIC_API_URL;

async function jsonFetch(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const msg = await res.text().catch(() => res.statusText);
    throw new Error(msg || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function predictOne(payload) {
  return jsonFetch(`${API}/predict-one`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function predictBatchFile(file) {
  const fd = new FormData();
  fd.append("file", file);
  return jsonFetch(`${API}/predict-batch-file`, {
    method: "POST",
    body: fd,
  });
}
export async function sendFeedback(payload) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
export async function getTemplateCsv() {
  const res = await fetch(`${API}/csv-template`);
  if (!res.ok) throw new Error("Impossible de télécharger le template");
  const blob = await res.blob();
  return blob;
}

export async function getStats() {
  return jsonFetch(`${API}/stats`);
}

export async function getFeedbackStats() {
  return jsonFetch(`${API}/feedback-stats`);
}
