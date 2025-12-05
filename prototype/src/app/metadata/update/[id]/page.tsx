"use client";

import { use, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { MetadataForm } from "@/features/metadata/components/MetadataForm";
import { useMetadataItem, useUpdateMetadata } from "@/features/metadata/hooks/useMetadata";

export default function UpdateMetadataPage({ params }: { params: Promise<{ id: string }> }) {
    const router = useRouter();
    const [id, setId] = useState<string>("");

    useEffect(() => {
        params.then((resolvedParams) => {
            setId(resolvedParams.id);
        });
    }, [params]);

    const { data: metadata, isLoading: isFetching } = useMetadataItem(id);
    const updateMetadataMutation = useUpdateMetadata();

    if (isFetching) {
        return <div>Loading...</div>;
    }

    if (!metadata) {
        return <div>Metadata not found</div>;
    }

    return (
        <div className="max-w-2xl mx-auto py-8">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Update Metadata</h1>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Update existing metadata information.
                </p>
            </div>
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <MetadataForm
                    initialData={metadata}
                    onSubmit={(data) => {
                        updateMetadataMutation.mutate(data, {
                            onSuccess: () => {
                                router.push(`/metadata/view/${id}`);
                            },
                        });
                    }}
                    onCancel={() => router.back()}
                    isLoading={updateMetadataMutation.isPending}
                    submitLabel="Update Metadata"
                />
            </div>
        </div>
    );
}
