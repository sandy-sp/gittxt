import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 15000,
});

interface ScanParams {
  repo: string;
  branch?: string;
}

interface ScanResult {
  data?: any;
  error?: string;
}

export async function scanRepository({ repo, branch }: ScanParams): Promise<ScanResult> {
  const payload = {
    repo_url: `https://github.com/${repo}`,
    branch: branch || 'main',
    output_format: ['txt', 'json'],
    create_zip: true,
    lite_mode: false,
    tree_depth: 2,
  };

  try {
    const response = await apiClient.post('/scan', payload);
    return { data: response.data };
  } catch (err: any) {
    console.error('Scan API error:', err?.response?.data || err.message);
    return {
      error:
        err?.response?.data?.detail ||
        'An unexpected error occurred while scanning the repository.',
    };
  }
}
