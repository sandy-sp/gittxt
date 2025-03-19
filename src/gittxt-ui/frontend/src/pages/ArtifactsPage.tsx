// src/pages/ArtifactsPage.tsx
import { useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useEffect, useState } from "react";
import { getArtifact } from "@/services/api";
import { useToast } from "@/components/ToastProvider";

export default function ArtifactsPage() {
  const { scanId } = useParams();
  const { toast } = useToast();

  const [markdown, setMarkdown] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const fileTypes = ["txt", "json", "md", "zip"];

  useEffect(() => {
    const fetchMarkdown = async () => {
      try {
        const res = await getArtifact(scanId!, "md");
        const blob = await res.data.text();
        setMarkdown(blob);
      } catch {
        setMarkdown("⚠️ Failed to load markdown preview.");
      }
    };
    fetchMarkdown();
  }, [scanId]);

  const handleDownload = async (type: string) => {
    try {
      setLoading(true);
      const res = await getArtifact(scanId!, type);
      const blob = new Blob([res.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `scan_${scanId}.${type === "zip" ? "zip" : type}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch {
      toast({
        title: "Download failed",
        description: `Could not download ${type.toUpperCase()} artifact.`,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-20 space-y-8">
      <h2 className="text-3xl font-semibold">Artifacts for Scan #{scanId}</h2>

      <Card>
        <CardContent className="p-6 space-y-4">
          <p className="text-sm text-gray-600">Download Outputs:</p>
          <div className="flex flex-wrap gap-4">
            {fileTypes.map((type) => (
              <Button
                key={type}
                onClick={() => handleDownload(type)}
                disabled={loading}
              >
                {loading ? "..." : `Download ${type.toUpperCase()}`}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {markdown && (
        <Card>
          <CardContent className="p-6 space-y-4">
            <h3 className="text-lg font-semibold">Markdown Preview</h3>
            <div className="prose max-w-none border p-4 bg-gray-50 rounded-md">
              <pre className="whitespace-pre-wrap text-sm">{markdown}</pre>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
