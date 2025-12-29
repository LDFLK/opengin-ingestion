"use client";

import { useEffect, useState } from "react";
import styles from "./Results.module.css";

interface ResultsProps {
    jobId: string | null;
}

interface FileItem {
    name: string;
    path: string;
}

interface FileNode {
    name: string;
    path: string;
    type: "file" | "directory";
    children?: FileNode[];
}

interface ResultsData {
    status: string;
    error: string | null;
    metadata: Record<string, unknown>;
    files: {
        csv: FileItem[];
        metadata: FileItem[];
        system: FileNode;
    };
}

export default function Results({ jobId }: ResultsProps) {
    const [data, setData] = useState<ResultsData | null>(null);
    const [activeTab, setActiveTab] = useState<"csv" | "metadata" | "system">("csv");
    const [selectedFile, setSelectedFile] = useState<string | null>(null);
    const [fileContent, setFileContent] = useState<string | null>(null);

    const handleSelectFile = (path: string | null) => {
        setSelectedFile(path);
        setFileContent(null);
    };

    // Poll for results
    useEffect(() => {
        if (!jobId) return;

        const interval = setInterval(async () => {
            try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/results/${jobId}`);
                if (response.ok) {
                    const result: ResultsData = await response.json();
                    setData(result);
                }
            } catch (error) {
                console.error("Polling error", error);
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [jobId]);

    // Fetch file content
    useEffect(() => {
        if (!selectedFile) return;

        const fetchContent = async () => {
            try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/file?path=${encodeURIComponent(selectedFile)}`);
                if (response.ok) {
                    const text = await response.text();
                    setFileContent(text);
                } else {
                    setFileContent("Error loading file content.");
                }
            } catch {
                setFileContent("Error loading file content.");
            }
        };

        fetchContent();
    }, [selectedFile]);

    const handleDownloadFile = (e: React.MouseEvent, path: string, name: string) => {
        e.stopPropagation();
        const link = document.createElement('a');
        link.href = `${process.env.NEXT_PUBLIC_API_URL}/api/file?path=${encodeURIComponent(path)}`;
        link.download = name;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleDownloadAll = () => {
        if (!jobId) return;
        window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/api/download-all/${jobId}`;
    };

    if (!jobId) return null;

    const renderFileTree = (node: FileNode) => {
        if (node.type === "file") {
            return (
                <div
                    key={node.path}
                    className={`${styles.fileItem} ${selectedFile === node.path ? styles.activeFile : ''}`}
                    onClick={() => handleSelectFile(node.path)}
                >
                    <span className={styles.fileName}>📄 {node.name}</span>
                    <button
                        className={styles.downloadBtn}
                        onClick={(e) => handleDownloadFile(e, node.path, node.name)}
                        title="Download"
                    >
                        ⬇
                    </button>
                </div>
            );
        }
        return (
            <div key={node.path} className={styles.dirItem}>
                <div className={styles.dirName}>📁 {node.name}</div>
                <div className={styles.dirChildren}>
                    {node.children?.map(renderFileTree)}
                </div>
            </div>
        );
    };

    const renderTabContent = () => {
        if (!data || !data.files) return <p>Waiting for data...</p>;

        const items = activeTab === "csv" ? data.files.csv :
            activeTab === "metadata" ? data.files.metadata : [];

        if (activeTab === "system") {
            return (
                <div className={styles.tree}>
                    {renderFileTree(data.files.system)}
                </div>
            );
        }

        return (
            <div className={styles.list}>
                {items.length === 0 && <p>No files found.</p>}
                {items.map((f: FileItem) => (
                    <div
                        key={f.path}
                        className={`${styles.fileItem} ${selectedFile === f.path ? styles.activeFile : ''}`}
                        onClick={() => handleSelectFile(f.path)}
                    >
                        <span className={styles.fileName}>{f.name}</span>
                        <button
                            className={styles.downloadBtn}
                            onClick={(e) => handleDownloadFile(e, f.path, f.name)}
                            title="Download"
                        >
                            ⬇
                        </button>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.headerLeft}>
                    <h3>Extraction Results</h3>
                    <span className={`${styles.status} ${data?.status === "COMPLETED" ? styles.success : ''}`}>
                        {data?.status || "PENDING"}
                    </span>
                </div>
                <button className={styles.downloadAllBtn} onClick={handleDownloadAll}>
                    Download All (Zip)
                </button>
            </div>

            <div className={styles.mainLayout}>
                <div className={styles.leftPanel}>
                    <div className={styles.tabs}>
                        <button
                            className={`${styles.tab} ${activeTab === 'csv' ? styles.activeTab : ''}`}
                            onClick={() => setActiveTab('csv')}
                        >
                            CSV
                        </button>
                        <button
                            className={`${styles.tab} ${activeTab === 'metadata' ? styles.activeTab : ''}`}
                            onClick={() => setActiveTab('metadata')}
                        >
                            Metadata
                        </button>
                        <button
                            className={`${styles.tab} ${activeTab === 'system' ? styles.activeTab : ''}`}
                            onClick={() => setActiveTab('system')}
                        >
                            System
                        </button>
                    </div>
                    <div className={styles.fileList}>
                        {renderTabContent()}
                    </div>
                </div>

                <div className={styles.rightPanel}>
                    {selectedFile ? (
                        <>
                            <div className={styles.contentHeader}>
                                <span>Viewing: {selectedFile.split('/').pop()}</span>
                                <button
                                    className={styles.downloadBtnHeader}
                                    onClick={(e) => handleDownloadFile(e, selectedFile, selectedFile.split('/').pop()!)}
                                >
                                    Download
                                </button>
                            </div>
                            <pre className={styles.fileContent}>{fileContent}</pre>
                        </>
                    ) : (
                        <div className={styles.placeholder}>Select a file to view content</div>
                    )}
                </div>
            </div>
        </div>
    );
}
