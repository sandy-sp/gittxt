import React, { useState } from "react";
import { getRepoTree } from "../services/apiService";

export default function Tree() {
  const [repoUrl, setRepoUrl] = useState("https://github.com/sandy-sp/gittxt.git");
  const [tree, setTree] = useState(null);
  const [extensions, setExtensions] = useState([]);

  const handleTreeFetch = async () => {
    try {
      const data = await getRepoTree(repoUrl);
      if (data.success) {
        setTree(data.tree);
        setExtensions(data.file_extensions);
      } else {
        alert("Error retrieving tree");
      }
    } catch (e) {
      alert("Tree fetch failed: " + e.message);
    }
  };

  return (
    <div style={{ padding: "1.5rem" }}>
      <h2>Repo Tree Viewer</h2>
      <input 
        value={repoUrl} 
        onChange={(e) => setRepoUrl(e.target.value)} 
        style={{ width: "400px" }} 
      />
      <button onClick={handleTreeFetch} style={{ marginLeft: "1rem" }}>
        Fetch Tree
      </button>
      {tree && (
        <>
          <pre style={{ marginTop: "1rem" }}>{JSON.stringify(tree, null, 2)}</pre>
          <p>Detected extensions: {extensions.join(", ")}</p>
        </>
      )}
    </div>
  );
}
