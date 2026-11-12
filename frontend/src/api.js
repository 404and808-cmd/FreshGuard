
const API_BASE = "http://127.0.0.1:8000";

export async function getClaimHistory(claimId) {
  const response = await fetch(
    `${API_BASE}/history/${encodeURIComponent(claimId)}`
  );

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `History request failed: ${response.status}`);
  }

  return response.json();
}
