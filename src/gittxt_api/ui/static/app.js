// src/gittxt_api/ui/static/app.js

const initialForm = document.getElementById("initialForm");
const filterForm = document.getElementById("filterForm");

const repoInput = document.getElementById("repo_url");
const statusDiv = document.getElementById("status");
const resultDiv = document.getElementById("result");
const summarySection = document.getElementById("summarySection");
const summaryOutput = document.getElementById("summaryOutput");
const filePreview = document.getElementById("filePreview");

let repo_url = "";
let latest_output_dir = "";

// ======== PHASE 1: INITIAL SCAN ========

initialForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  repo_url = repoInput.value.trim();
  if (!repo_url) return;

  resetUI();
  statusDiv.innerHTML = "⏳ Starting initial scan...";

  const payload = {
    repo_url: repo_url,
    output_format: ["txt"], // only .txt for preview
    lite_mode: true,
    create_zip: false
  };

  const taskId = await startScan(payload);
  pollStatus(taskId, { phase: 1 });
});

// ======== PHASE 2: FILTERED SCAN ========

filterForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  statusDiv.innerHTML = "⏳ Applying filters and re-scanning...";

  const formData = new FormData(filterForm);
  const payload = {
    repo_url: repo_url,
    output_format: formData.getAll("output_format"),
    lite_mode: formData.get("lite_mode") === "on",
    create_zip: formData.get("create_zip") === "on",
    include_patterns: parseCSV(formData.get("include_patterns")),
    exclude_patterns: parseCSV(formData.get("exclude_patterns")),
    tree_depth: parseOptionalInt(formData.get("tree_depth")),
    size_limit: parseOptionalInt(formData.get("size_limit"))
  };

  const taskId = await startScan(payload);
  pollStatus(taskId, { phase: 2 });
});

// ======== SHARED HELPERS ========

async function startScan(payload) {
  const res = await fetch("/scan/async", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const { task_id } = await res.json();
  return task_id;
}

function pollStatus(taskId, { phase }) {
  const interval = setInterval(async () => {
    const res = await fetch(`/scan/status/${taskId}`);
    const data = await res.json();

    if (data.status === "completed") {
      clearInterval(interval);
      fetchResult(taskId, phase);
    } else if (data.status === "failed") {
      clearInterval(interval);
      statusDiv.innerHTML = `❌ Scan failed: ${data.error}`;
    } else {
      statusDiv.innerHTML = `🔄 Scan in progress... (${data.status})`;
    }
  }, 2000);
}

async function fetchResult(taskId, phase) {
  const res = await fetch(`/scan/result/${taskId}`);
  const data = await res.json();

  latest_output_dir = data.output_dir;
  statusDiv.innerHTML = "✅ Scan complete!";

  if (phase === 1) {
    summaryOutput.innerHTML = `
      <p><strong>Repo:</strong> ${data.repo_name}</p>
      <p><strong>Total Files:</strong> ${data.total_files}</p>
      <p><strong>Total Size:</strong> ${humanFileSize(data.total_size_bytes)}</p>
      <p><strong>Estimated Tokens:</strong> ${data.estimated_tokens}</p>
    `;
    summarySection.classList.remove("hidden");
    filterForm.classList.remove("hidden");
    await loadPreviewFile(data.output_files);
  }

  if (phase === 2) {
    const zipFile = data.output_files.find(f => f.endsWith(".zip"));
    const zipLink = zipFile
      ? `<p><a href="/zip?output_dir=${encodeURIComponent(data.output_dir)}" target="_blank" download>
          📥 Download ZIP Output
        </a></p>`
      : "";

    resultDiv.innerHTML = `
      <h3>📦 Filtered Scan Summary</h3>
      <p><strong>Total Files:</strong> ${data.total_files}</p>
      <p><strong>Total Size:</strong> ${humanFileSize(data.total_size_bytes)}</p>
      <p><strong>Estimated Tokens:</strong> ${data.estimated_tokens}</p>
      ${zipLink}
      <p><strong>Outputs:</strong></p>
      <ul>${data.output_files.map(f => `<li><code>${f}</code></li>`).join("")}</ul>
      <p><strong>Skipped Files:</strong> ${data.skipped_files.length}</p>
    `;
    resultDiv.classList.remove("hidden");
  }
}

async function loadPreviewFile(outputFiles) {
  const txtPath = outputFiles.find(p => p.endsWith(".txt"));
  if (!txtPath) {
    filePreview.innerText = "No previewable .txt file found.";
    return;
  }

  try {
    const raw = await fetch(txtPath);
    const content = await raw.text();
    filePreview.innerText = content.slice(0, 10000) + "\n..."; // limit preview
  } catch (err) {
    filePreview.innerText = "❌ Failed to load preview.";
  }
}

function parseCSV(val) {
  if (!val || !val.trim()) return null;
  return val.split(",").map(v => v.trim()).filter(Boolean);
}

function parseOptionalInt(val) {
  return val ? parseInt(val, 10) : null;
}

function humanFileSize(bytes) {
  const thresh = 1024;
  if (Math.abs(bytes) < thresh) return bytes + ' B';
  const units = ['KB', 'MB', 'GB'];
  let u = -1;
  do {
    bytes /= thresh;
    ++u;
  } while (Math.abs(bytes) >= thresh && u < units.length - 1);
  return bytes.toFixed(1) + ' ' + units[u];
}

function resetUI() {
  statusDiv.innerHTML = "";
  summarySection.classList.add("hidden");
  resultDiv.classList.add("hidden");
  filterForm.classList.add("hidden");
  summaryOutput.innerHTML = "";
  filePreview.innerText = "";
}
