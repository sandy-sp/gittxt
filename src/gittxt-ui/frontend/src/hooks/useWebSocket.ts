// src/hooks/useWebSocket.ts
import { useEffect, useState } from "react";

export function useWebSocketProgress(scanId: string) {
  const [status, setStatus] = useState("queued");
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/wsprogress/ws/${scanId}`);

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.event === "progress") {
        setStatus(msg.data.status);
        setProgress(msg.data.progress);
        setCurrentFile(msg.data.current_file);
      } else if (msg.event === "done") {
        setStatus("done");
        setProgress(100);
        setDone(true);
      } else if (msg.event === "error") {
        setStatus("error");
      }
    };

    return () => ws.close();
  }, [scanId]);

  return { status, progress, currentFile, done };
}
