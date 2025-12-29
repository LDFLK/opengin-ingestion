"use client";

import { useState } from "react";
import styles from "./Upload.module.css";

interface UploadProps {
    onUploadComplete: (fileId: string, filename: string) => void;
}

export default function Upload({ onUploadComplete }: UploadProps) {
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files || e.target.files.length === 0) return;

        const file = e.target.files[0];
        setUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/upload`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || "Upload failed");
            }

            const data = await response.json();
            onUploadComplete(data.file_id, data.filename);
        } catch (err: any) {
            setError(err.message || "Something went wrong");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className={styles.container}>
            <h3>Upload Document</h3>
            <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                disabled={uploading}
                className={styles.input}
            />
            {uploading && <p>Uploading...</p>}
            {error && <p className={styles.error}>{error}</p>}
        </div>
    );
}
