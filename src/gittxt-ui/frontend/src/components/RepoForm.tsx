// src/components/RepoForm.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import FileTypeSelector from "./FileTypeSelector";
import RepoTree from "./RepoTree";
import { useScanContext } from "@/context/ScanContext";
import { useToast } from "@/components/ToastProvider";
import { getRepoTree, startScan } from "@/services/api";

export default function RepoForm() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const { setRepoUrl, setScanId, setFileTypes, setOutputFormat } = useScanContext();

  const [repoUrlInput, setRepoUrlInput] = useState("");
  const [branch, setBranch] = useState("");
  const [fileTypesInput, setFileTypesInput] = useState<string[]>([]);
  const [formats, setFormats] = useState<string[]>(["txt", "json"]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrlInput || !repoUrlInput.startsWith("https://github.com/")) {
      toast({
        title: "Invalid URL",
        description: "Please enter a valid GitHub URL.",
        variant: "destructive",
      });
      return;
    }

    const payload = {
      repo_url: repoUrlInput,
      branch: branch || null,
      file_types: fileTypesInput.join(",") || "code,docs",
      output_format: formats.join(","),
      include_patterns: [],
      exclude_patterns: [".git", "node_modules"],
      size_limit: null,
    };

    try {
      setLoading(true);

      // Sync context before API call
      setRepoUrl(repoUrlInput);
      setFileTypes(fileTypesInput);
      setOutputFormat(formats);

      const res = await axios.post("http://localhost:8000/scans", payload);
      setScanId(res.data.scan_id);
      navigate(`/progress/${res.data.scan_id}`);
    } catch (err: any) {
      toast({
        title: "Scan Failed",
        description: "Check backend logs or connection.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium">Repository URL</label>
        <Input
          required
          value={repoUrlInput}
          onChange={(e) => setRepoUrlInput(e.target.value)}
          placeholder="https://github.com/user/repo.git"
          disabled={loading}
        />
      </div>
      <div>
        <label className="block text-sm font-medium">Branch (optional)</label>
        <Input
          value={branch}
          onChange={(e) => setBranch(e.target.value)}
          placeholder="e.g., main"
          disabled={loading}
        />
      </div>

      {repoUrlInput && (
        <>
          <FileTypeSelector
            repoUrl={repoUrlInput}
            selected={fileTypesInput}
            setSelected={setFileTypesInput}
          />
          <RepoTree repoUrl={repoUrlInput} />
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
                disabled={loading}
              />
              <span>{fmt.toUpperCase()}</span>
            </label>
          ))}
        </div>
      </div>

      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? "Starting Scan..." : "Start Scan"}
      </Button>
    </form>
  );
}
