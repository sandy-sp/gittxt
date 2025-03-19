// src/components/RepoTree.tsx
import { useEffect, useState } from "react";
import axios from "axios";

interface Props {
  repoUrl: string;
}

interface TreeNode {
  name: string;
  type: "file" | "dir";
  children?: TreeNode[];
}

export default function RepoTreeViewer({ repoUrl }: Props) {
  const [tree, setTree] = useState<TreeNode | null>(null);

  useEffect(() => {
    if (!repoUrl) return;

    axios.post("http://localhost:8000/scans/tree", { repo_url: repoUrl })
      .then((res) => setTree(res.data.tree))
      .catch(() => setTree(null));
  }, [repoUrl]);

  const renderTree = (node: TreeNode) => (
    <li className="ml-4 list-none" key={node.name}>
      <span className="text-sm">{node.type === "dir" ? "📁" : "📄"} {node.name}</span>
      {node.children && (
        <ul>{node.children.map(renderTree)}</ul>
      )}
    </li>
  );

  if (!tree) return null;

  return (
    <div className="mt-6">
      <p className="text-sm font-medium mb-2">Repo Tree Preview:</p>
      <ul className="border rounded-md p-3 bg-white max-h-96 overflow-y-auto">
        {renderTree(tree)}
      </ul>
    </div>
  );
}
