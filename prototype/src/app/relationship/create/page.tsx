"use client";

import { useRouter } from "next/navigation";
import { RelationshipForm } from "@/features/relationship/components/RelationshipForm";
import { useCreateRelationship } from "@/features/relationship/hooks/useRelationships";

export default function CreateRelationshipPage() {
    const router = useRouter();
    const createRelationshipMutation = useCreateRelationship();

    return (
        <div className="max-w-2xl mx-auto py-8">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create New Relationship</h1>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Add a new relationship between entities.
                </p>
            </div>
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <RelationshipForm
                    onSubmit={(data) => {
                        createRelationshipMutation.mutate(data, {
                            onSuccess: () => {
                                router.push("/relationship");
                            },
                        });
                    }}
                    onCancel={() => router.back()}
                    isLoading={createRelationshipMutation.isPending}
                    submitLabel="Create Relationship"
                />
            </div>
        </div>
    );
}
