// src/pages/Progress.tsx
import { useParams, useNavigate } from "react-router-dom";
import { useWebSocketProgress } from "../hooks/useWebSocket";
import { Progress as ProgressBar } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import axios from "axios";
import { useToast } from "@/components/ToastProvider";

export default function Progress() {
  const { scanId } = useParams();
  const { status, progress, currentFile, done } = useWebSocketProgress(scanId!);
  const [startTime] = useState(Date.now());
  const navigate = useNavigate();
  const { toast } = useToast();

  const cancelScan = async () => {
    try {
      await axios.delete(`http://localhost:8000/scans/${scanId}/close`);
      toast({
        title: "Scan canceled",
        description: "The scan was successfully canceled.",
        variant: "default",
      });
      navigate("/scan");
    } catch {
      toast({
        title: "Cancel failed",
        description: "Unable to cancel scan, check backend logs.",
        variant: "destructive",
      });
    }
  };

  const estimateETA = () => {
    if (progress < 5 || progress >= 100) return null;
    const elapsed = (Date.now() - startTime) / 1000;
    const eta = elapsed / (progress / 100) - elapsed;
    return `${Math.round(eta)} sec`;
  };

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
          <p className="text-sm text-gray-600 truncate">
            Current file: {currentFile || "Waiting..."}
          </p>
          {progress > 0 && progress < 100 && (
            <p className="text-xs text-gray-500">ETA: {estimateETA()}</p>
          )}
          <div className="space-y-2">
            {status === "running" && (
              <Button
                variant="destructive"
                onClick={cancelScan}
                className="w-full"
              >
                Cancel Scan
              </Button>
            )}
            {done && (
              <Button asChild className="w-full mt-4">
                <a href={`/artifacts/${scanId}`}>View Artifacts</a>
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
