// src/pages/Config.tsx
import { useEffect, useState } from "react";
import axios from "axios";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { toast } from "react-toastify";

export default function Config() {
  const [outputDir, setOutputDir] = useState("");
  const [loggingLevel, setLoggingLevel] = useState("INFO");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get("http://localhost:8000/config").then((res) => {
      setOutputDir(res.data.output_dir);
      setLoggingLevel(res.data.logging_level);
      setLoading(false);
    });
  }, []);

  const handleSave = async () => {
    try {
      await axios.post("http://localhost:8000/config", {
        output_dir: outputDir,
        logging_level: loggingLevel,
      });
      toast.success("Config updated successfully!");
    } catch (err) {
      toast.error("Failed to update config.");
    }
  };

  if (loading) return <div className="text-center py-20">Loading config...</div>;

  return (
    <div className="max-w-xl mx-auto py-20 space-y-6">
      <h2 className="text-3xl font-semibold">Global Config</h2>

      <Card>
        <CardContent className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium">Output Directory</label>
            <Input
              value={outputDir}
              onChange={(e) => setOutputDir(e.target.value)}
              placeholder="/path/to/output"
            />
          </div>

          <div>
            <label className="block text-sm font-medium">Logging Level</label>
            <select
              value={loggingLevel}
              onChange={(e) => setLoggingLevel(e.target.value)}
              className="w-full mt-1 px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
            >
              {['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'].map((lvl) => (
                <option key={lvl} value={lvl}>{lvl}</option>
              ))}
            </select>
          </div>

          <Button onClick={handleSave} className="w-full">Save Config</Button>
        </CardContent>
      </Card>
    </div>
  );
}
