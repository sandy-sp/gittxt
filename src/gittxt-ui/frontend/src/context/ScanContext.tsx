// src/context/ScanContext.tsx
import { createContext, useContext, useState, ReactNode } from "react";

interface ScanContextProps {
  repoUrl: string;
  setRepoUrl: (url: string) => void;
  scanId: string;
  setScanId: (id: string) => void;
  fileTypes: string[];
  setFileTypes: (types: string[]) => void;
  outputFormat: string[];
  setOutputFormat: (formats: string[]) => void;
}

const ScanContext = createContext<ScanContextProps | undefined>(undefined);

export const ScanProvider = ({ children }: { children: ReactNode }) => {
  const [repoUrl, setRepoUrl] = useState("");
  const [scanId, setScanId] = useState("");
  const [fileTypes, setFileTypes] = useState<string[]>(["code", "docs"]);
  const [outputFormat, setOutputFormat] = useState<string[]>(["txt", "json"]);

  return (
    <ScanContext.Provider
      value={{
        repoUrl,
        setRepoUrl,
        scanId,
        setScanId,
        fileTypes,
        setFileTypes,
        outputFormat,
        setOutputFormat,
      }}
    >
      {children}
    </ScanContext.Provider>
  );
};

export const useScanContext = (): ScanContextProps => {
  const context = useContext(ScanContext);
  if (!context) {
    throw new Error("useScanContext must be used within a ScanProvider");
  }
  return context;
};
