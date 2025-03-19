// src/components/FileTypeSelector.tsx
import { useEffect, useState } from "react";
import axios from "axios";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/components/ToastProvider";

interface Props {
  repoUrl: string;
  selected: string[];
  setSelected: (types: string[]) => void;
}

export default function FileTypeSelector({ repoUrl, selected, setSelected }: Props) {
  const [availableTypes, setAvailableTypes] = useState<string[]>([]);
  const { toast } = useToast();

  useEffect(() => {
    if (!repoUrl) return;

    axios.post("http://localhost:8000/scans/tree", { repo_url: repoUrl })
      .then((res) => {
        const extList = res.data.file_extensions || [];
        setAvailableTypes(extList);
      })
      .catch(() => {
        toast({
          title: "Tree Fetch Failed",
          description: "Could not load available file types.",
          variant: "destructive",
        });
      });
  }, [repoUrl]);

  const toggle = (ext: string) => {
    if (selected.includes(ext)) {
      setSelected(selected.filter((e) => e !== ext));
    } else {
      setSelected([...selected, ext]);
    }
  };

  return (
    <div className="space-y-4 mt-4">
      <p className="text-sm text-gray-600 mb-1">File Types (auto-fetched):</p>
      <div className="flex flex-wrap gap-3">
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
