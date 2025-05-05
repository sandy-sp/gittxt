import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api, { ScanSummaryResp } from "@/api";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import ProgressBar from "@/components/ProgressBar";
import { Table, TableHead, TableHeader, TableBody, TableRow, TableCell } from "@/components/ui/table";

export default function ScanDashboard() {
  const { id } = useParams();
  const [data, setData] = useState<ScanSummaryResp | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const poll = setInterval(async () => {
      try {
        const { data } = await api.get<ScanSummaryResp>(`/v1/summary/${id}`);
        setData(data);
        if (data.done) clearInterval(poll);
      } finally {
        setLoading(false);
      }
    }, 4000);
    return () => clearInterval(poll);
  }, [id]);

  if (loading) return <Skeleton className="w-full h-32" />;

  if (!data) return <p>No data available.</p>;

  const progressValue = data.files.length > 0 ? Math.min(data.files.length * 5, 90) : 0;
  const progressLabel = progressValue === 90 ? "Almost done" : `${progressValue}% completed`;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">
        {data.repository?.name ?? id}
      </h2>

      {data.done
        ? <ResultsTable files={data.files} scanId={id!} />
        : (
          <div>
            <ProgressBar value={progressValue} aria-label={progressLabel} />
            <p className="text-sm text-gray-600 mt-2">{progressLabel}</p>
          </div>
        )
      }
    </div>
  );
}

function ResultsTable({ files, scanId }: { files: ScanSummaryResp["files"]; scanId: string }) {
  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>File</TableHead>
            <TableHead className="text-right">Tokens</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {files.map(f => (
            <TableRow key={f.path}>
              <TableCell className="truncate max-w-[240px]">{f.path}</TableCell>
              <TableCell className="text-right">{f.tokens}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <div className="flex gap-2">
        {["txt", "json", "md", "zip"].map(fmt => (
          <Button key={fmt} asChild size="sm">
            <a href={`${import.meta.env.VITE_API_URL}/v1/download/${scanId}?format=${fmt}`} target="_blank">
              {fmt.toUpperCase()}
            </a>
          </Button>
        ))}
      </div>
    </>
  );
}
