"use client";

import { use, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { EntityForm } from "@/features/entity/components/EntityForm";
import { useEntity, useUpdateEntity } from "@/features/entity/hooks/useEntities";

export default function UpdateEntityPage({ params }: { params: Promise<{ id: string }> }) {
    const router = useRouter();
    const [id, setId] = useState<string>("");

    useEffect(() => {
        params.then((resolvedParams) => {
            setId(resolvedParams.id);
        });
    }, [params]);

    const { data: entity, isLoading: isFetching } = useEntity(id);
    const updateEntityMutation = useUpdateEntity();

    if (isFetching) {
        return <div>Loading...</div>;
    }

    if (!entity) {
        return <div>Entity not found</div>;
    }

    return (
        <div className="max-w-2xl mx-auto py-8">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Update Entity</h1>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Update existing entity information.
                </p>
            </div>
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <EntityForm
                    initialData={entity}
                    onSubmit={(data) => {
                        updateEntityMutation.mutate(data, {
                            onSuccess: () => {
                                router.push(`/entity/view/${id}`);
                            },
                        });
                    }}
                    onCancel={() => router.back()}
                    isLoading={updateEntityMutation.isPending}
                    submitLabel="Update Entity"
                />
            </div>
        </div>
    );
}
