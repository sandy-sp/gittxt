import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [fileTypes, setFileTypes] = useState('code,docs');
  const [outputFormat, setOutputFormat] = useState('txt,json');
  const [scanResult, setScanResult] = useState(null);

  const onScan = async () => {
    setScanResult(null);
    try {
      const { data } = await axios.post('http://localhost:8000/scan', {
        repo_url: repoUrl,
        file_types: fileTypes,
        output_format: outputFormat
      });
      setScanResult(data);
    } catch (err) {
      alert(`Error scanning: ${err?.response?.data?.detail || err.message}`);
    }
  };

  return (
    <div style={{ padding: '1rem' }}>
      <h1>Gittxt Web UI</h1>
      <div>
        <input
          placeholder="Enter repo URL or local path"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          style={{ width: '300px' }}
        />
      </div>
      <div>
        <label>File Types: </label>
        <input
          placeholder="code,docs"
          value={fileTypes}
          onChange={(e) => setFileTypes(e.target.value)}
        />
      </div>
      <div>
        <label>Output Format: </label>
        <input
          placeholder="txt,json"
          value={outputFormat}
          onChange={(e) => setOutputFormat(e.target.value)}
        />
      </div>
      <button onClick={onScan} disabled={!repoUrl}>
        Scan
      </button>

      {scanResult && (
        <div style={{ marginTop: '1rem' }}>
          <pre>{JSON.stringify(scanResult, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
