"use client";

import { useRouter } from "next/navigation";
import { Plus, Search, Eye, Pencil } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Table, Column } from "@/components/ui/Table";
import { useRelationships } from "@/features/relationship/hooks/useRelationships";
import { Relationship } from "@/services/relationshipService";

export default function RelationshipPage() {
    const router = useRouter();
    const { data: relationships = [], isLoading } = useRelationships();

    const columns: Column<Relationship>[] = [
        {
            header: "ID",
            accessorKey: "id",
            className: "font-medium text-gray-900 dark:text-white",
            cell: (relationship) => (
                <button
                    onClick={() => router.push(`/relationship/view/${relationship.id}`)}
                    className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300 hover:underline"
                >
                    {relationship.id}
                </button>
            ),
        },
        {
            header: "Key",
            accessorKey: "key",
            className: "font-medium text-gray-900 dark:text-white",
        },
        {
            header: "Related Entity ID",
            accessorKey: "relatedEntityId",
        },
        {
            header: "Start Time",
            accessorKey: "startTime",
        },
        {
            header: "End Time",
            accessorKey: "endTime",
        },
        {
            header: "Actions",
            cell: (relationship) => (
                <div className="flex space-x-2">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => router.push(`/relationship/view/${relationship.id}`)}
                        title="View"
                    >
                        <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => router.push(`/relationship/update/${relationship.id}`)}
                        title="Edit"
                    >
                        <Pencil className="h-4 w-4" />
                    </Button>
                </div>
            ),
        },
    ];

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Relationships</h1>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        Manage connections between entities.
                    </p>
                </div>
                <Button onClick={() => router.push("/relationship/create")} leftIcon={<Plus className="h-4 w-4" />}>
                    New Relationship
                </Button>
            </div>

            {/* Search Bar (Mock) */}
            <div className="relative rounded-md shadow-sm max-w-md">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" aria-hidden="true" />
                </div>
                <input
                    type="text"
                    name="search"
                    id="search"
                    className="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md py-2 dark:bg-gray-800 dark:border-gray-700"
                    placeholder="Search relationships..."
                />
            </div>

            {/* Table */}
            <Table
                data={relationships}
                columns={columns}
                keyExtractor={(item) => item.id}
                isLoading={isLoading}
                pagination={{
                    currentPage: 1,
                    totalPages: 1,
                    onPageChange: () => { },
                }}
            />
        </div>
    );
}
