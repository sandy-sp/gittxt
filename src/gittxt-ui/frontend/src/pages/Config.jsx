import React, { useEffect, useState } from "react";
import { getConfig, updateConfig } from "../services/apiService";

export default function Config() {
  const [config, setConfig] = useState(null);
  const [loggingLevel, setLoggingLevel] = useState("");

  useEffect(() => {
    getConfig().then((data) => {
      setConfig(data);
      setLoggingLevel(data.logging_level || "");
    });
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    const payload = { logging_level: loggingLevel };
    const result = await updateConfig(payload);
    alert(JSON.stringify(result, null, 2));
  };

  if (!config) return <p>Loading config...</p>;

  return (
    <div style={{ padding: "1.5rem" }}>
      <h2>Gittxt Configuration</h2>
      <div><strong>Output Directory:</strong> {config.output_dir}</div>
      <div><strong>File Types:</strong> {config.file_types}</div>
      <hr />
      <h4>Update Logging Level</h4>
      <form onSubmit={handleSave}>
        <select value={loggingLevel} onChange={(e) => setLoggingLevel(e.target.value)}>
          <option value="INFO">INFO</option>
          <option value="DEBUG">DEBUG</option>
          <option value="WARNING">WARNING</option>
          <option value="ERROR">ERROR</option>
        </select>
        <button type="submit" style={{ marginLeft: "1rem" }}>Update</button>
      </form>
    </div>
  );
}
