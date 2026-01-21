"use client";

import { useRouter } from "next/navigation";
import { AttributeForm } from "@/features/attribute/components/AttributeForm";
import { useCreateAttribute } from "@/features/attribute/hooks/useAttributes";

export default function CreateAttributePage() {
    const router = useRouter();
    const createAttributeMutation = useCreateAttribute();

    return (
        <div className="max-w-2xl mx-auto py-8">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create New Attribute</h1>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Add a new attribute record.
                </p>
            </div>
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <AttributeForm
                    onSubmit={(data) => {
                        createAttributeMutation.mutate(data, {
                            onSuccess: () => {
                                router.push("/attribute");
                            },
                        });
                    }}
                    onCancel={() => router.back()}
                    isLoading={createAttributeMutation.isPending}
                    submitLabel="Create Attribute"
                />
            </div>
        </div>
    );
}
