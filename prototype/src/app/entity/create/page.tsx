"use client";

import { useRouter } from "next/navigation";
import { EntityForm } from "@/features/entity/components/EntityForm";
import { useCreateEntity } from "@/features/entity/hooks/useEntities";

export default function CreateEntityPage() {
    const router = useRouter();
    const createEntityMutation = useCreateEntity();

    return (
        <div className="max-w-2xl mx-auto py-8">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create New Entity</h1>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Add a new entity to the system.
                </p>
            </div>
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <EntityForm
                    onSubmit={(data) => {
                        createEntityMutation.mutate(data, {
                            onSuccess: () => {
                                router.push("/entity");
                            },
                        });
                    }}
                    onCancel={() => router.back()}
                    isLoading={createEntityMutation.isPending}
                    submitLabel="Create Entity"
                />
            </div>
        </div>
    );
}
