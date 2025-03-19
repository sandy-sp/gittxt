// src/components/ScanProgress.tsx
import { Progress as ProgressBar } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Props {
  status: string;
  progress: number;
  currentFile: string;
  done: boolean;
  scanId: string;
}

export default function ScanProgress({ status, progress, currentFile, done, scanId }: Props) {
  const color = status === "done" ? "text-green-600" : status === "error" ? "text-red-600" : "text-gray-800";

  return (
    <Card>
      <CardContent className="space-y-4 p-6">
        <div>
          <p className="text-sm text-gray-700 mb-1">Status:</p>
          <p className={`font-semibold text-lg capitalize ${color}`}>{status}</p>
        </div>
        <ProgressBar value={progress} />
        <div className="flex items-center gap-2">
          <p className="text-sm text-gray-600 truncate">Current file:</p>
          <Badge variant="outline">{currentFile || "Waiting..."}</Badge>
        </div>
        {done && (
          <Button asChild className="w-full mt-4">
            <a href={`/artifacts/${scanId}`}>View Artifacts</a>
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
