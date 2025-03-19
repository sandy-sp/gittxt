// src/components/RepoTree.tsx
import { useEffect, useState } from "react";
import axios from "axios";
import { Alert, AlertTitle } from "@/components/ui/alert";

interface Props {
  repoUrl: string;
}

interface TreeNode {
  name: string;
  type: "directory" | "file";
  children?: TreeNode[];
}

export default function RepoTree({ repoUrl }: Props) {
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!repoUrl) return;

    axios.post("http://localhost:8000/scans/tree", { repo_url: repoUrl })
      .then((res) => {
        setTree(res.data.tree);
        setError(false);
      })
      .catch(() => setError(true));
  }, [repoUrl]);

  const renderTree = (node: TreeNode) => (
    <li key={node.name} className="ml-4 list-none">
      <span className="text-sm">{node.type === "directory" ? "📁" : "📄"} {node.name}</span>
      {node.children && (
        <ul>{node.children.map(renderTree)}</ul>
      )}
    </li>
  );

  if (error) {
    return (
      <Alert variant="destructive" className="mt-4">
        <AlertTitle>Repo tree could not be loaded</AlertTitle>
      </Alert>
    );
  }

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
