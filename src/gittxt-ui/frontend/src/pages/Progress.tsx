// src/pages/Progress.tsx
import { useParams } from "react-router-dom";
import { useWebSocketProgress } from "../hooks/useWebSocket";
import { Progress as ProgressBar } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function Progress() {
  const { scanId } = useParams();
  const { status, progress, currentFile, done } = useWebSocketProgress(scanId!);

  return (
    <div className="max-w-2xl mx-auto py-20 space-y-6">
      <h2 className="text-3xl font-semibold">Scan Progress</h2>
      <Card>
        <CardContent className="space-y-4 p-6">
          <div>
            <p className="text-sm text-gray-700 mb-1">Status:</p>
            <p className="font-semibold text-lg capitalize">{status}</p>
          </div>
          <ProgressBar value={progress} />
          <p className="text-sm text-gray-600 truncate">Current file: {currentFile || "Waiting..."}</p>
          {done && (
            <Button asChild className="w-full mt-4">
              <a href={`/artifacts/${scanId}`}>View Artifacts</a>
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
