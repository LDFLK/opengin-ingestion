"use client";

import { use, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AttributeForm } from "@/features/attribute/components/AttributeForm";
import { useAttribute, useUpdateAttribute } from "@/features/attribute/hooks/useAttributes";

export default function UpdateAttributePage({ params }: { params: Promise<{ id: string }> }) {
    const router = useRouter();
    const [id, setId] = useState<string>("");

    useEffect(() => {
        params.then((resolvedParams) => {
            setId(resolvedParams.id);
        });
    }, [params]);

    const { data: attribute, isLoading: isFetching } = useAttribute(id);
    const updateAttributeMutation = useUpdateAttribute();

    if (isFetching) {
        return <div>Loading...</div>;
    }

    if (!attribute) {
        return <div>Attribute not found</div>;
    }

    return (
        <div className="max-w-2xl mx-auto py-8">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Update Attribute Value</h1>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Update specific attribute record.
                </p>
            </div>
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <AttributeForm
                    initialData={attribute}
                    onSubmit={(data) => {
                        updateAttributeMutation.mutate(data, {
                            onSuccess: () => {
                                router.push(`/attribute/view/${data.id}`);
                            },
                        });
                    }}
                    onCancel={() => router.back()}
                    isLoading={updateAttributeMutation.isPending}
                    submitLabel="Update Attribute"
                />
            </div>
        </div>
    );
}
