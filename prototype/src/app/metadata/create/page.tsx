"use client";

import { useRouter } from "next/navigation";
import { MetadataForm } from "@/features/metadata/components/MetadataForm";
import { useCreateMetadata } from "@/features/metadata/hooks/useMetadata";

export default function CreateMetadataPage() {
    const router = useRouter();
    const createMetadataMutation = useCreateMetadata();

    return (
        <div className="max-w-2xl mx-auto py-8">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create New Metadata</h1>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Add a new metadata item.
                </p>
            </div>
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <MetadataForm
                    onSubmit={(data) => {
                        createMetadataMutation.mutate(data, {
                            onSuccess: () => {
                                router.push("/metadata");
                            },
                        });
                    }}
                    onCancel={() => router.back()}
                    isLoading={createMetadataMutation.isPending}
                    submitLabel="Create Metadata"
                />
            </div>
        </div>
    );
}
