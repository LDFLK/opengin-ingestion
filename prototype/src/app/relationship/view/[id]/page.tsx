"use client";

import { use, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { useRelationship } from "@/features/relationship/hooks/useRelationships";
import { Pencil, ArrowLeft } from "lucide-react";

export default function ViewRelationshipPage({ params }: { params: Promise<{ id: string }> }) {
    const router = useRouter();
    const [id, setId] = useState<string>("");

    useEffect(() => {
        params.then((resolvedParams) => {
            setId(resolvedParams.id);
        });
    }, [params]);

    const { data: relationship, isLoading, error } = useRelationship(id);

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error || !relationship) {
        return <div>Relationship not found</div>;
    }

    return (
        <div className="max-w-2xl mx-auto py-8">
            <div className="mb-6 flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Relationship Details</h1>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        View relationship information.
                    </p>
                </div>
                <div className="flex space-x-3">
                    <Button variant="secondary" onClick={() => router.back()} leftIcon={<ArrowLeft className="h-4 w-4" />}>
                        Back
                    </Button>
                    <Button onClick={() => router.push(`/relationship/update/${relationship.id}`)} leftIcon={<Pencil className="h-4 w-4" />}>
                        Edit
                    </Button>
                </div>
            </div>

            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 space-y-6">
                <div>
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">ID</h3>
                    <p className="mt-1 text-lg text-gray-900 dark:text-white">{relationship.id}</p>
                </div>
                <div>
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Key</h3>
                    <p className="mt-1 text-lg text-gray-900 dark:text-white">{relationship.key}</p>
                </div>
                <div>
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Related Entity ID</h3>
                    <p className="mt-1 text-lg text-gray-900 dark:text-white">{relationship.relatedEntityId}</p>
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Start Time</h3>
                        <p className="mt-1 text-lg text-gray-900 dark:text-white">{relationship.startTime}</p>
                    </div>
                    <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">End Time</h3>
                        <p className="mt-1 text-lg text-gray-900 dark:text-white">{relationship.endTime || "-"}</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
