import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div style={{ padding: "1.5rem" }}>
      <h1>Welcome to Gittxt UI</h1>
      <p>A frontend interface for scanning GitHub repositories with Gittxt.</p>
      <ul style={{ marginTop: "1rem" }}>
        <li><Link to="/config">🔧 Configure Gittxt</Link></li>
        <li><Link to="/scan">🚀 Start a Repository Scan</Link></li>
        <li><Link to="/tree">🌳 View Repo Tree</Link></li>
      </ul>
    </div>
  );
}
