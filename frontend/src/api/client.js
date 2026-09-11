const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchAgents() {
  const res = await fetch(`${API_BASE}/agents`);
  return res.json();
}

export async function fetchAgent(agentId) {
  const res = await fetch(`${API_BASE}/agents/${agentId}`);
  if (!res.ok) throw new Error("Agent not found");
  return res.json();
}

export async function runAgent(agentId, prompt) {
  const res = await fetch(`${API_BASE}/agents/${agentId}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Run failed");
  }
  return res.json();
}

export async function fetchRuns() {
  const res = await fetch(`${API_BASE}/runs`);
  return res.json();
}

export async function fetchRun(runId) {
  const res = await fetch(`${API_BASE}/runs/${runId}`);
  if (!res.ok) throw new Error("Run not found");
  return res.json();
}

export async function fetchRunTools(runId) {
  const res = await fetch(`${API_BASE}/runs/${runId}/tools`);
  if (!res.ok) throw new Error("Run not found");
  return res.json();
}

export async function fetchRunMessages(runId) {
  const res = await fetch(`${API_BASE}/runs/${runId}/messages`);
  if (!res.ok) throw new Error("Run not found");
  return res.json();
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE}/metrics`);
  return res.json();
}
