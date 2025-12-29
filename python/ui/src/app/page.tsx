"use client";

import { useState } from "react";
import Upload from "@/components/Upload";
import Configuration from "@/components/Configuration";
import Results from "@/components/Results";
import styles from "./page.module.css";

export default function Home() {
  const [fileId, setFileId] = useState<string | null>(null);
  const [filename, setFilename] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [presetMetadata, setPresetMetadata] = useState<string | undefined>(undefined);
  const [presetPrompt, setPresetPrompt] = useState<string | undefined>(undefined);

  const handleUploadComplete = (fid: string, fname: string) => {
    setFileId(fid);
    setFilename(fname);
  };

  const handleExtract = (jid: string) => {
    setJobId(jid);
  };

  const handleQuickStart = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/quick-setup`);
      if (!response.ok) throw new Error("Quick setup failed");

      const data = await response.json();
      setFileId(data.file_id);
      setFilename(data.filename);
      setPresetMetadata(data.metadata);
      setPresetPrompt(data.prompt);
    } catch (error) {
      console.error("Quick Start Error:", error);
      alert("Failed to load Quick Start configuration.");
    }
  };

  return (
    <main className={styles.main}>
      <h1 className={styles.title}>OpenGIN Ingestion UI</h1>

      <div className={styles.grid}>
        <div>
          <Upload onUploadComplete={handleUploadComplete} />
          <button onClick={handleQuickStart} className={styles.quickStartButton}>
            🚀 Quick Start (Sample PDF & Config)
          </button>
        </div>

        <Configuration
          fileId={fileId}
          filename={filename}
          onExtract={handleExtract}
          presetMetadata={presetMetadata}
          presetPrompt={presetPrompt}
        />

        <Results jobId={jobId} />
      </div>
    </main>
  );
}
