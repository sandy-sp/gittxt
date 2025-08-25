import axios from 'axios';

// Define the base URL for your FastAPI backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// ============================================================================
// Data Models
// These interfaces match the Pydantic models in your FastAPI application.
// ============================================================================

export interface ScanRequest {
    repo_path: string;
    exclude_dirs?: string[];
    output_formats?: string[];
    include_patterns?: string[];
    exclude_patterns?: string[];
    create_zip?: boolean;
    lite?: boolean;
    sync_ignore?: boolean;
    size_limit?: number;
    branch?: string;
    tree_depth?: number;
    docs_only?: boolean;
    skip_tree?: boolean;
  }
  
  export interface SummaryData {
      total_files: number;
      total_size: number;
      estimated_tokens: number;
      file_type_breakdown: { [key: string]: number };
      tokens_by_type: { [key: string]: number };
      formatted: {
          total_size: string;
          estimated_tokens: string;
          tokens_by_type: { [key: string]: string };
      };
  }
  
  export interface ScanResponse {
      scan_id: string;
      repo_name: string;
      num_textual_files: number;
      num_non_textual_files: number;
      artifact_dir: string;
      message: string;
      summary: SummaryData;
  }
  
  export interface FileInspectResponse {
    content: string;
    file_path: string;
    language: string;
    size_bytes: number;
  }

// ============================================================================
// API Calls
// ============================================================================

/**
 * Initiates a new scan request to the backend.
 * @param requestData The data for the scan request.
 * @returns A promise that resolves with the scan response.
 */
export const performScan = async (requestData: ScanRequest): Promise<ScanResponse> => {
    try {
        const response = await api.post<ScanResponse>("/v1/scan/", requestData);
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error) && error.response) {
            throw new Error(error.response.data.detail || 'An unexpected error occurred during the scan.');
        }
        throw new Error('Network error or server is unreachable.');
    }
};

/**
 * Fetches the summary of a completed scan.
 * @param scanId The ID of the scan to retrieve.
 * @returns A promise that resolves with the scan summary response.
 */
export const getScanSummary = async (scanId: string): Promise<ScanResponse> => {
    try {
        const response = await api.get<ScanResponse>(`/v1/summary/${scanId}`);
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error) && error.response) {
            throw new Error(error.response.data.detail || 'Failed to fetch scan summary.');
        }
        throw new Error('Network error or server is unreachable.');
    }
};

/**
 * Downloads the ZIP artifact for a given scan ID.
 * @param scanId The ID of the scan to download.
 * @returns A promise that resolves when the download is complete.
 */
export const downloadArtifact = async (scanId: string): Promise<void> => {
    try {
        const response = await api.get(`/v1/download/${scanId}/zip`, {
            responseType: 'blob', // Important for downloading files
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `gittxt_scan_${scanId}.zip`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    } catch (error) {
        if (axios.isAxiosError(error) && error.response) {
            throw new Error(error.response.data.detail || 'Failed to download artifact.');
        }
        throw new Error('Network error or server is unreachable.');
    }
};

/**
 * Fetches the content of a specific file from a scan.
 * @param scanId The ID of the scan.
 * @param filePath The path of the file within the repository.
 * @returns A promise that resolves with the file content.
 */
export const getInspectionContent = async (scanId: string, filePath: string): Promise<FileInspectResponse> => {
  try {
      const response = await api.post<FileInspectResponse>(`/v1/inspect/`, {
          scan_id: scanId,
          file_path: filePath
      });
      return response.data;
  } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
          throw new Error(error.response.data.detail || 'Failed to fetch file content.');
      }
      throw new Error('Network error or server is unreachable.');
  }
};