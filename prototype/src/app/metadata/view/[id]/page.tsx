"use client";

import { use, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { useMetadataItem } from "@/features/metadata/hooks/useMetadata";
import { Pencil, ArrowLeft } from "lucide-react";

export default function ViewMetadataPage({ params }: { params: Promise<{ id: string }> }) {
    const router = useRouter();
    const [id, setId] = useState<string>("");

    useEffect(() => {
        params.then((resolvedParams) => {
            setId(resolvedParams.id);
        });
    }, [params]);

    const { data: metadata, isLoading, error } = useMetadataItem(id);

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error || !metadata) {
        return <div>Metadata not found</div>;
    }

    return (
        <div className="max-w-2xl mx-auto py-8">
            <div className="mb-6 flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Metadata Details</h1>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        View metadata information.
                    </p>
                </div>
                <div className="flex space-x-3">
                    <Button variant="secondary" onClick={() => router.back()} leftIcon={<ArrowLeft className="h-4 w-4" />}>
                        Back
                    </Button>
                    <Button onClick={() => router.push(`/metadata/update/${metadata.id}`)} leftIcon={<Pencil className="h-4 w-4" />}>
                        Edit
                    </Button>
                </div>
            </div>

            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 space-y-6">
                <div>
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">ID</h3>
                    <p className="mt-1 text-lg text-gray-900 dark:text-white">{metadata.id}</p>
                </div>
                <div>
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Key</h3>
                    <p className="mt-1 text-lg text-gray-900 dark:text-white">{metadata.key}</p>
                </div>
                <div>
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Value</h3>
                    <p className="mt-1 text-lg text-gray-900 dark:text-white">{metadata.value}</p>
                </div>
            </div>
        </div>
    );
}
