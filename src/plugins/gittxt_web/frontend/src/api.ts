import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

export interface ScanStartResp { scan_id: string }
export interface ScanSummaryResp {
  done: boolean;
  repository: { name: string; url?: string };
  files: { path: string; tokens: number }[];
}
export interface InspectResp {
  summary: {
    total_tokens: number;
    total_files: number;
    language_breakdown: Record<string, number>;
  };
}

export const inspectRepo = (repoUrl: string) =>
  api.post<InspectResp>("/v1/inspect", { repo_url: repoUrl });

export default api;
