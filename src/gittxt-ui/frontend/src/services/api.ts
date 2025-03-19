// src/services/api.ts
import axios from "axios";

const API_BASE = "http://localhost:8000";

export async function getRepoTree(repoUrl: string, branch?: string) {
  const res = await axios.post(`${API_BASE}/scans/tree`, { repo_url: repoUrl, branch });
  return res.data;
}

export async function startScan(payload: {
  repo_url: string;
  branch?: string;
  file_types: string;
  output_format: string;
  include_patterns?: string[];
  exclude_patterns?: string[];
  size_limit?: number | null;
}) {
  const res = await axios.post(`${API_BASE}/scans`, payload);
  return res.data;
}

export async function getScanStatus(scanId: string) {
  const res = await axios.get(`${API_BASE}/scans/${scanId}`);
  return res.data;
}

export async function closeScan(scanId: string) {
  const res = await axios.delete(`${API_BASE}/scans/${scanId}/close`);
  return res.data;
}

export async function getConfig() {
  const res = await axios.get(`${API_BASE}/config`);
  return res.data;
}

export async function updateConfig(updates: { output_dir?: string; logging_level?: string }) {
  const res = await axios.post(`${API_BASE}/config`, updates);
  return res.data;
}

export async function getArtifact(scanId: string, type: "json" | "txt" | "md" | "zip") {
  const res = await axios.get(`${API_BASE}/artifacts/${scanId}/${type}`, { responseType: "blob" });
  return res;
}
