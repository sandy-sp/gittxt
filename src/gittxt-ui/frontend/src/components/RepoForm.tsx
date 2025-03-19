// src/components/RepoForm.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import FileTypeSelector from "./FileTypeSelector";
import RepoTree from "./RepoTree";

export default function RepoForm() {
  const [repoUrl, setRepoUrl] = useState("");
  const [branch, setBranch] = useState("");
  const [fileTypes, setFileTypes] = useState<string[]>([]);
  const [formats, setFormats] = useState<string[]>(["txt", "json"]);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload = {
      repo_url: repoUrl,
      branch: branch || null,
      file_types: fileTypes.join(","),
      output_format: formats.join(","),
      include_patterns: [],
      exclude_patterns: [".git", "node_modules"],
      size_limit: null,
    };

    try {
      const res = await axios.post("http://localhost:8000/scans", payload);
      navigate(`/progress/${res.data.scan_id}`);
    } catch (err) {
      alert("Scan request failed. Check backend logs.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium">Repository URL</label>
        <Input
          required
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/user/repo.git"
        />
      </div>
      <div>
        <label className="block text-sm font-medium">Branch (optional)</label>
        <Input
          value={branch}
          onChange={(e) => setBranch(e.target.value)}
          placeholder="e.g., main"
        />
      </div>

      {/* Dynamic file type fetcher */}
      {repoUrl && (
        <>
          <FileTypeSelector repoUrl={repoUrl} selected={fileTypes} setSelected={setFileTypes} />
          <RepoTree repoUrl={repoUrl} />
        </>
      )}

      <div>
        <label className="block text-sm font-medium mb-2">Output Formats</label>
        <div className="flex gap-4">
          {['txt', 'json', 'md', 'zip'].map((fmt) => (
            <label key={fmt} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formats.includes(fmt)}
                onChange={() =>
                  formats.includes(fmt)
                    ? setFormats(formats.filter((f) => f !== fmt))
                    : setFormats([...formats, fmt])
                }
              />
              <span>{fmt.toUpperCase()}</span>
            </label>
          ))}
        </div>
      </div>

      <Button type="submit" className="w-full">Start Scan</Button>
    </form>
  );
}
