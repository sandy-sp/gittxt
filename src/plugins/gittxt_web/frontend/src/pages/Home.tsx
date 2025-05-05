import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { ScanStartResp } from "@/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import InspectDialog from "@/components/InspectDialog";
import { inspectRepo } from "@/api";
import { Skeleton } from "@/components/ui/skeleton";

export default function Home() {
  const nav = useNavigate();
  const [repo, setRepo] = useState("");
  const [open, setOpen] = useState(false);
  const [summary, setSummary] = useState<InspectResp["summary"]>();
  const [loading, setLoading] = useState(false);

  const startScan = async () => {
    setLoading(true);
    try {
      const { data } = await api.post<ScanStartResp>("/v1/scan", { repo_url: repo });
      nav(`/scan/${data.scan_id}`);
    } finally {
      setLoading(false);
    }
  };

  const preview = async () => {
    setOpen(true);
    setSummary(undefined); // Reset
    setLoading(true);
    try {
      const { data } = await inspectRepo(repo);
      setSummary(data.summary);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="mx-auto max-w-xl">
      <CardContent className="space-y-4 p-6">
        <h2 className="text-xl font-semibold">Scan a public repository</h2>
        <Input placeholder="https://github.com/user/repo" value={repo} onChange={e => setRepo(e.target.value)} />
        <div className="flex gap-2 flex-wrap">
          <Button disabled={!repo || loading} onClick={startScan}>{loading ? "Loading…" : "Start Scan"}</Button>
          <Button variant="secondary" asChild><a href="/upload">Upload ZIP instead</a></Button>
          <Button variant="outline" disabled={!repo || loading} onClick={preview}>{loading ? "Loading…" : "Preview Summary"}</Button>
        </div>
      </CardContent>
      {loading && <Skeleton className="h-6 w-full mt-4" />}
      <InspectDialog open={open} onOpenChange={setOpen} summary={summary} />
    </Card>
  );
}
