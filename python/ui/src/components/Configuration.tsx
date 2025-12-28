"use client";

import { useState, useEffect } from "react";
import styles from "./Configuration.module.css";

interface ConfigurationProps {
    fileId: string | null;
    filename: string | null;
    onExtract: (jobId: string) => void;
    presetMetadata?: string;
    presetPrompt?: string;
}

export default function Configuration({ fileId, filename, onExtract, presetMetadata, presetPrompt }: ConfigurationProps) {
    const [apiKey, setApiKey] = useState("");
    const [metadata, setMetadata] = useState("");
    const [prompt, setPrompt] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Effect to update state when presets change (Quick Start)
    useEffect(() => {
        if (presetMetadata) setMetadata(presetMetadata);
    }, [presetMetadata]);

    useEffect(() => {
        if (presetPrompt) setPrompt(presetPrompt);
    }, [presetPrompt]);

    const handleExtract = async () => {
        if (!fileId) return;
        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append("file_id", fileId);
        formData.append("api_key", apiKey);
        formData.append("metadata", metadata);
        formData.append("prompt", prompt);

        try {
            const response = await fetch("http://localhost:8001/api/extract", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Extraction failed");
            }

            const data = await response.json();
            onExtract(data.job_id);
        } catch (err: any) {
            setError(err.message || "Failed to start extraction");
        } finally {
            setLoading(false);
        }
    };

    if (!fileId) return null;

    return (
        <div className={styles.container}>
            <h3>Configuration for {filename}</h3>

            <div className={styles.field}>
                <label>Google API Key:</label>
                <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className={styles.input}
                />
            </div>

            <div className={styles.field}>
                <label>Metadata (YAML):</label>
                <textarea
                    value={metadata}
                    onChange={(e) => setMetadata(e.target.value)}
                    rows={5}
                    className={styles.textarea}
                />
            </div>

            <div className={styles.field}>
                <label>Extraction Prompt:</label>
                <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    rows={3}
                    className={styles.textarea}
                />
            </div>

            <button onClick={handleExtract} disabled={loading} className={styles.button}>
                {loading ? "Extracting..." : "Run Extraction"}
            </button>

            {error && <p className={styles.error}>{error}</p>}
        </div>
    );
}
