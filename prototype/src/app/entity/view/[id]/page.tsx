"use client";

import { use, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { useEntity } from "@/features/entity/hooks/useEntities";
import { Pencil, ArrowLeft } from "lucide-react";

export default function ViewEntityPage({ params }: { params: Promise<{ id: string }> }) {
    const router = useRouter();
    const [id, setId] = useState<string>("");

    useEffect(() => {
        params.then((resolvedParams) => {
            setId(resolvedParams.id);
        });
    }, [params]);

    const { data: entity, isLoading, error } = useEntity(id);

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error || !entity) {
        return <div>Entity not found</div>;
    }

    console.log("view.id.Entity:", entity);

    return (
        <div className="max-w-2xl mx-auto py-8">
            <div className="mb-6 flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Entity Details</h1>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        View entity information.
                    </p>
                </div>
                <div className="flex space-x-3">
                    <Button variant="secondary" onClick={() => router.back()} leftIcon={<ArrowLeft className="h-4 w-4" />}>
                        Back
                    </Button>
                    <Button onClick={() => router.push(`/entity/update/${entity.id}`)} leftIcon={<Pencil className="h-4 w-4" />}>
                        Edit
                    </Button>
                </div>
            </div>

            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 space-y-6">
                <div>
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">ID</h3>
                    <p className="mt-1 text-lg text-gray-900 dark:text-white">{entity.id}</p>
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Major Kind</h3>
                        <p className="mt-1 text-lg text-gray-900 dark:text-white">{entity.kind.major}</p>
                    </div>
                    <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Minor Kind</h3>
                        <p className="mt-1 text-lg text-gray-900 dark:text-white">{entity.kind.minor}</p>
                    </div>
                </div>
                <div>
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Name</h3>
                    <p className="mt-1 text-lg text-gray-900 dark:text-white">{entity.name.value}</p>
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Start Time</h3>
                        <p className="mt-1 text-lg text-gray-900 dark:text-white">{entity.created}</p>
                    </div>
                    <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">End Time</h3>
                        <p className="mt-1 text-lg text-gray-900 dark:text-white">{entity.terminated || "-"}</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
