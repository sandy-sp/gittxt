// src/pages/Scan.tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const formSchema = z.object({
  repo_url: z.string().url("Invalid URL"),
  branch: z.string().optional(),
  file_types: z.array(z.string()),
  output_format: z.array(z.string()),
});

export default function Scan() {
  const navigate = useNavigate();
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      repo_url: "",
      branch: "",
      file_types: [],
      output_format: [],
    },
  });

  const fileTypes = ["code", "docs", "images", "csv"];
  const outputFormats = ["txt", "json", "md", "zip"];
  const watchFileTypes = watch("file_types");
  const watchFormats = watch("output_format");

  const toggleCheckbox = (field: "file_types" | "output_format", value: string) => {
    const current = watch(field);
    if (current.includes(value)) {
      setValue(field, current.filter((v: string) => v !== value));
    } else {
      setValue(field, [...current, value]);
    }
  };

  const onSubmit = async (data: any) => {
    try {
      const res = await axios.post("http://localhost:8000/scans", data);
      navigate(`/progress/${res.data.scan_id}`);
    } catch (err) {
      alert("Scan failed. Check API.");
    }
  };

  return (
    <div className="max-w-xl mx-auto py-20 space-y-6">
      <h2 className="text-3xl font-semibold mb-4">Start New Scan</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium">Repository URL</label>
          <Input {...register("repo_url")} placeholder="https://github.com/..." />
          {errors.repo_url && <p className="text-red-500 text-sm">{errors.repo_url.message as string}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium">Branch (optional)</label>
          <Input {...register("branch")} placeholder="main / develop / etc." />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">File Types</label>
          <div className="flex gap-4 flex-wrap">
            {fileTypes.map((type) => (
              <label key={type} className="flex items-center space-x-2">
                <Checkbox checked={watchFileTypes.includes(type)} onCheckedChange={() => toggleCheckbox("file_types", type)} />
                <span>{type}</span>
              </label>
            ))}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Output Formats</label>
          <div className="flex gap-4 flex-wrap">
            {outputFormats.map((fmt) => (
              <label key={fmt} className="flex items-center space-x-2">
                <Checkbox checked={watchFormats.includes(fmt)} onCheckedChange={() => toggleCheckbox("output_format", fmt)} />
                <span>{fmt}</span>
              </label>
            ))}
          </div>
        </div>
        <Button type="submit" className="w-full">Start Scan</Button>
      </form>
    </div>
  );
}
