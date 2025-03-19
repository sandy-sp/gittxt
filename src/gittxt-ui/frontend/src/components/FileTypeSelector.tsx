// src/components/FileTypeSelector.tsx
import { useEffect, useState } from "react";
import axios from "axios";
import { Checkbox } from "@/components/ui/checkbox";

interface Props {
  repoUrl: string;
  selected: string[];
  setSelected: (types: string[]) => void;
}

export default function FileTypeSelector({ repoUrl, selected, setSelected }: Props) {
  const [availableTypes, setAvailableTypes] = useState<string[]>([]);

  useEffect(() => {
    if (!repoUrl) return;

    axios.post("http://localhost:8000/scans/tree", { repo_url: repoUrl })
      .then((res) => {
        const extList = res.data.extensions || [];
        setAvailableTypes(extList);
      })
      .catch(() => setAvailableTypes([]));
  }, [repoUrl]);

  const toggle = (ext: string) => {
    if (selected.includes(ext)) {
      setSelected(selected.filter((e) => e !== ext));
    } else {
      setSelected([...selected, ext]);
    }
  };

  return (
    <div className="space-y-2">
      <p className="text-sm text-gray-600 mb-1">File Types (auto-fetched):</p>
      <div className="flex gap-3 flex-wrap">
        {availableTypes.map((ext) => (
          <label key={ext} className="flex items-center space-x-2">
            <Checkbox checked={selected.includes(ext)} onCheckedChange={() => toggle(ext)} />
            <span>{ext}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
