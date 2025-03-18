import React, { useState, useRef } from "react";
import { startScan, getArtifactUrl } from "../services/apiService";
import ProgressBar from "../components/ProgressBar";

export default function Scan() {
  const [repoUrl, setRepoUrl] = useState("https://github.com/sandy-sp/gittxt.git");
  const [scanId, setScanId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("idle");
  const [currentFile, setCurrentFile] = useState("");
  const wsRef = useRef(null);

  const handleStartScan = async () => {
    setStatus("queued");
    setProgress(0);
    setCurrentFile("");
    setScanId(null);

    const payload = {
      repo_url: repoUrl,
      file_types: "code,docs",
      output_format: "txt,json,md",
      include_patterns: [],
      exclude_patterns: [".git", "node_modules"],
      size_limit: null,
      branch: null,
    };

    try {
      const data = await startScan(payload);
      setScanId(data.scan_id);
      setStatus(data.status || "queued");
      openWebSocket(data.scan_id);
    } catch (err) {
      alert("Failed to start scan: " + err.message);
      setStatus("error");
    }
  };

  const openWebSocket = (scanId) => {
    const wsUrl = `ws://127.0.0.1:8000/wsprogress/ws/${scanId}`;
    const socket = new WebSocket(wsUrl);
    wsRef.current = socket;

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.event === "progress") {
        setProgress(msg.data.progress || 0);
        setStatus(msg.data.status);
        setCurrentFile(msg.data.current_file || "");
      } else if (msg.event === "done" || msg.event === "error") {
        setStatus(msg.event);
        setProgress(100);
        socket.close();
      }
    };
  };

  const handleDownload = (type) => {
    if (!scanId) return;
    const url = getArtifactUrl(scanId, type);
    window.open(url, "_blank");
  };

  return (
    <div style={{ padding: "1.5rem" }}>
      <h2>Start Gittxt Scan</h2>
      <input 
        value={repoUrl} 
        onChange={(e) => setRepoUrl(e.target.value)} 
        style={{ width: "400px" }} 
      />
      <button onClick={handleStartScan} style={{ marginLeft: "1rem" }}>
        Start
      </button>
      <hr />
      <p>Status: {status}</p>
      <ProgressBar value={progress} />
      {currentFile && <p>File: {currentFile}</p>}

      {status === "done" && (
        <div style={{ marginTop: "1rem" }}>
          <button onClick={() => handleDownload("txt")}>Download .txt</button>
          <button onClick={() => handleDownload("json")} style={{ marginLeft: "1rem" }}>
            Download .json
          </button>
          <button onClick={() => handleDownload("md")} style={{ marginLeft: "1rem" }}>
            Download .md
          </button>
          <button onClick={() => handleDownload("zip")} style={{ marginLeft: "1rem" }}>
            Download .zip
          </button>
        </div>
      )}
    </div>
  );
}
