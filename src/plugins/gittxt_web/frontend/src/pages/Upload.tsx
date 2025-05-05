import { useNavigate } from "react-router-dom";
import api, { ScanStartResp } from "@/api";
import UploadDropzone from "@/components/UploadDropzone";
import { Card, CardContent } from "@/components/ui/card";
import { useState } from "react";
import { Progress } from "@/components/ui/progress";
import { Alert } from "@/components/ui/alert"; // Assuming an Alert component exists

export default function Upload() {
  const nav = useNavigate();
  const [pct, setPct] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    setError(null); // Reset error state
    const form = new FormData();
    form.append("file", file);
    try {
      const { data } = await api.post<ScanStartResp>("/v1/upload", form, {
        onUploadProgress: e => setPct(Math.round((e.loaded * 100) / (e.total ?? 1))),
      });
      nav(`/scan/${data.scan_id}`);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
      setPct(0); // Reset progress bar
    }
  };

  return (
    <Card className="mx-auto max-w-xl">
      <CardContent className="space-y-4 p-6">
        <h2 className="text-xl font-semibold">Upload a repo ZIP</h2>
        <UploadDropzone onFile={handleFile} />
        {pct > 0 && pct < 100 && <Progress value={pct} />}
        {error && <Alert variant="error">{error}</Alert>}
      </CardContent>
    </Card>
  );
}
