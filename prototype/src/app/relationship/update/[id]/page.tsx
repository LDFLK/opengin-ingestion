"use client";

import { use, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { RelationshipForm } from "@/features/relationship/components/RelationshipForm";
import { useRelationship, useUpdateRelationship } from "@/features/relationship/hooks/useRelationships";

export default function UpdateRelationshipPage({ params }: { params: Promise<{ id: string }> }) {
    const router = useRouter();
    const [id, setId] = useState<string>("");

    useEffect(() => {
        params.then((resolvedParams) => {
            setId(resolvedParams.id);
        });
    }, [params]);

    const { data: relationship, isLoading: isFetching } = useRelationship(id);
    const updateRelationshipMutation = useUpdateRelationship();

    if (isFetching) {
        return <div>Loading...</div>;
    }

    if (!relationship) {
        return <div>Relationship not found</div>;
    }

    return (
        <div className="max-w-2xl mx-auto py-8">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Update Relationship</h1>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Update existing relationship information.
                </p>
            </div>
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <RelationshipForm
                    initialData={relationship}
                    onSubmit={(data) => {
                        updateRelationshipMutation.mutate(data, {
                            onSuccess: () => {
                                router.push(`/relationship/view/${id}`);
                            },
                        });
                    }}
                    onCancel={() => router.back()}
                    isLoading={updateRelationshipMutation.isPending}
                    submitLabel="Update Relationship"
                />
            </div>
        </div>
    );
}
