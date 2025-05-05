import { useNavigate } from "react-router-dom";
import api, { ScanStartResp } from "@/api";
import UploadDropzone from "@/components/UploadDropzone";
import { Card, CardContent } from "@/components/ui/card";
import { useState } from "react";
import { Progress } from "@/components/ui/progress";

export default function Upload() {
  const nav = useNavigate();
  const [pct, setPct] = useState(0);

  const handleFile = async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    const { data } = await api.post<ScanStartResp>("/v1/upload", form, {
      onUploadProgress: e => setPct(Math.round((e.loaded * 100) / (e.total ?? 1))),
    });
    nav(`/scan/${data.scan_id}`);
  };

  return (
    <Card className="mx-auto max-w-xl">
      <CardContent className="space-y-4 p-6">
        <h2 className="text-xl font-semibold">Upload a repo ZIP</h2>
        <UploadDropzone onFile={handleFile} />
        {pct > 0 && pct < 100 && <Progress value={pct} />}
      </CardContent>
    </Card>
  );
}
