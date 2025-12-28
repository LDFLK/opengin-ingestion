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

  const handleUploadComplete = (fid: string, fname: string) => {
    setFileId(fid);
    setFilename(fname);
  };

  const handleExtract = (jid: string) => {
    setJobId(jid);
  };

  return (
    <main className={styles.main}>
      <h1 className={styles.title}>OpenGIN Ingestion UI</h1>

      <div className={styles.grid}>
        <Upload onUploadComplete={handleUploadComplete} />

        <Configuration
          fileId={fileId}
          filename={filename}
          onExtract={handleExtract}
        />

        <Results jobId={jobId} />
      </div>
    </main>
  );
}
