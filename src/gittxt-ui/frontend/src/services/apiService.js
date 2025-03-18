// src/services/apiService.js
const BASE_URL = process.env.REACT_APP_BACKEND_URL || "";

export async function getConfig() {
  const response = await fetch(`${BASE_URL}/config`);
  if (!response.ok) throw new Error("Failed to fetch config");
  return await response.json();
}

export async function updateConfig(payload) {
  const response = await fetch(`${BASE_URL}/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return await response.json();
}

export async function getRepoTree(repoUrl, branch = null) {
  const response = await fetch(`${BASE_URL}/scans/tree`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl, branch }),
  });
  return await response.json();
}

export async function startScan(payload) {
  const response = await fetch(`${BASE_URL}/scans`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return await response.json();
}

export async function getScanInfo(scanId) {
  const response = await fetch(`${BASE_URL}/scans/${scanId}`);
  return await response.json();
}

export async function closeScan(scanId) {
  const response = await fetch(`${BASE_URL}/scans/${scanId}/close`, {
    method: "DELETE",
  });
  return await response.json();
}

export function getArtifactUrl(scanId, type = "json") {
  return `${BASE_URL}/artifacts/${scanId}/${type}`;
}
