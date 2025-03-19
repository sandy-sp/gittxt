// src/pages/ArtifactsPage.tsx
import { useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useEffect, useState } from "react";
import axios from "axios";

export default function ArtifactsPage() {
  const { scanId } = useParams();
  const [markdown, setMarkdown] = useState<string>("");

  useEffect(() => {
    // Auto-load the Markdown file for preview
    axios.get(`http://localhost:8000/artifacts/${scanId}/md`)
      .then((res) => setMarkdown(res.data))
      .catch(() => setMarkdown("Failed to load markdown preview."));
  }, [scanId]);

  const fileTypes = ["txt", "json", "md", "zip"];

  return (
    <div className="max-w-3xl mx-auto py-20 space-y-8">
      <h2 className="text-3xl font-semibold">Artifacts for Scan #{scanId}</h2>

      <Card>
        <CardContent className="p-6 space-y-4">
          <p className="text-sm text-gray-600">Download Outputs:</p>
          <div className="flex flex-wrap gap-4">
            {fileTypes.map((type) => (
              <Button key={type} asChild>
                <a
                  href={`http://localhost:8000/artifacts/${scanId}/${type}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Download {type.toUpperCase()}
                </a>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {markdown && (
        <Card>
          <CardContent className="p-6 space-y-4">
            <h3 className="text-lg font-semibold">Markdown Preview</h3>
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm">{markdown}</pre>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
