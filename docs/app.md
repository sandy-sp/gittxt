<!-- Updated app.md with functional JavaScript for AWS Lambda integration -->

# 🧑‍💻 Gittxt Web Scanner

A static page that mimics the Streamlit plugin, powered by AWS Lambda.
Below is an HTML-based form for scanning GitHub repositories with Gittxt. The heavy lifting is handled by a backend AWS Lambda function.

<style>
  .gittxt-scanner {
    background: #111;
    color: #eee;
    padding: 24px;
    border-radius: 12px;
    font-family: 'Segoe UI', sans-serif;
    margin-bottom: 2rem;
  }
  .gittxt-scanner h2 {
    color: #ff9800;
    margin-bottom: 12px;
  }
  .gittxt-scanner label {
    display: block;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 5px;
  }
  .gittxt-scanner input,
  .gittxt-scanner select {
    width: 100%;
    padding: 8px 10px;
    background: #222;
    border: 1px solid #555;
    border-radius: 4px;
    color: #eee;
  }
  .gittxt-scanner .checkbox-line {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .gittxt-scanner .submit-btn {
    background: #e53935;
    color: #fff;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    border: none;
    margin-top: 20px;
  }
  #result-box {
    margin-top: 2rem;
    background: #222;
    padding: 1rem;
    border-radius: 6px;
    overflow-x: auto;
    white-space: pre-wrap;
  }
</style>

<div class="gittxt-scanner">
  <h2>GitHub Repository Scanner</h2>

  <label for="repoUrl">Repository URL</label>
  <input id="repoUrl" placeholder="https://github.com/username/repo" required />

  <label for="branch">Branch (optional)</label>
  <input id="branch" placeholder="main" />

  <label for="includePatterns">Include Patterns</label>
  <input id="includePatterns" value="**/*.py,**/*.md" />

  <label for="excludePatterns">Exclude Patterns</label>
  <input id="excludePatterns" value="tests/*,.vscode/*" />

  <label for="excludeDirs">Exclude Directories</label>
  <input id="excludeDirs" value="__pycache__,.git,node_modules" />

  <label for="sizeLimitMB">Max File Size (MB)</label>
  <input id="sizeLimitMB" type="number" value="10" min="1" />

  <label for="treeDepth">Tree Depth</label>
  <input id="treeDepth" type="number" value="3" min="1" />

  <div class="checkbox-line">
    <input type="checkbox" id="liteMode" /> <span>Lite Mode</span>
  </div>
  <div class="checkbox-line">
    <input type="checkbox" id="skipTree" /> <span>Skip Tree</span>
  </div>
  <div class="checkbox-line">
    <input type="checkbox" id="syncIgnore" /> <span>Use .gittxtignore</span>
  </div>
  <div class="checkbox-line">
    <input type="checkbox" id="docsOnly" /> <span>Docs Only</span>
  </div>
  <div class="checkbox-line">
    <input type="checkbox" id="createZip" /> <span>Create ZIP Bundle</span>
  </div>

  <button class="submit-btn" onclick="runScan()">Scan</button>
  <div id="result-box">
    <pre id="scanResult">Result will appear here...</pre>
  </div>
</div>

<script>
  async function runScan() {
    const repo_path = document.getElementById('repoUrl').value.trim();
    const branch = document.getElementById('branch').value.trim();

    if (!repo_path) {
      alert('Please enter a GitHub repo URL.');
      return;
    }

    const body = {
      repo_path,
      branch: branch || undefined,
      include_patterns: document.getElementById('includePatterns').value.split(',').map(s => s.trim()),
      exclude_patterns: document.getElementById('excludePatterns').value.split(',').map(s => s.trim()),
      exclude_dirs: document.getElementById('excludeDirs').value.split(',').map(s => s.trim()),
      size_limit: parseInt(document.getElementById('sizeLimitMB').value) * 1_000_000,
      tree_depth: parseInt(document.getElementById('treeDepth').value),
      lite: document.getElementById('liteMode').checked,
      skip_tree: document.getElementById('skipTree').checked,
      sync_ignore: document.getElementById('syncIgnore').checked,
      docs_only: document.getElementById('docsOnly').checked,
      create_zip: document.getElementById('createZip').checked
    };

    const resultEl = document.getElementById('scanResult');
    resultEl.textContent = '⏳ Scanning...';

    try {
      // TODO: Replace with actual API Gateway endpoint
      const lambdaUrl = "https://your-lambda-api.amazonaws.com/prod/scan";

      const res = await fetch(lambdaUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      if (!res.ok) {
        const err = await res.text();
        throw new Error(`Scan failed: ${res.status} - ${err}`);
      }

      const result = await res.json();
      resultEl.textContent = JSON.stringify(result, null, 2);
    } catch (err) {
      resultEl.textContent = `❌ Error: ${err.message}`;
    }
  }
</script>
