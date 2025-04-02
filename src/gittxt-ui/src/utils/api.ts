import axios from 'axios';

export async function scanRepository({ repo, branch }) {
  const payload = {
    repo_url: `https://github.com/${repo}`,
    branch: branch || 'main',
    output_format: ['txt', 'json'],
    create_zip: true,
    lite_mode: false,
    tree_depth: 2,
  };

  const res = await axios.post('http://localhost:8000/scan', payload);
  return res.data;
}
