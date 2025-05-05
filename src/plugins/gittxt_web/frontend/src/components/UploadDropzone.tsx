import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Button } from "@/components/ui/button";

export interface DropProps { onFile: (file: File) => void }

export default function UploadDropzone({ onFile }: DropProps) {
  const onDrop = useCallback((accepted: File[]) => {
    if (accepted.length) onFile(accepted[0]);
  }, [onFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: { "application/zip": [".zip"] } });

  return (
    <div {...getRootProps()} className="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors hover:border-primary">
      <input {...getInputProps()} />
      <p>{isDragActive ? "Drop it!" : "Drag & drop ZIP here, or click to select."}</p>
    </div>
  );
}
