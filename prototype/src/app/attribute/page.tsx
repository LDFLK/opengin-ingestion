"use client";

import { useRouter } from "next/navigation";
import { Plus, Search, Eye, Pencil } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Table, Column } from "@/components/ui/Table";
import { useAttributes } from "@/features/attribute/hooks/useAttributes";
import { Attribute } from "@/services/attributeService";

export default function AttributePage() {
    const router = useRouter();
    const { data: attributes = [], isLoading } = useAttributes();

    const columns: Column<Attribute>[] = [
        {
            header: "Name",
            accessorKey: "name",
            className: "font-medium text-gray-900 dark:text-white",
            cell: (item) => (
                <button
                    onClick={() => router.push(`/attribute/view/${item.id}`)}
                    className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300 hover:underline"
                >
                    {item.name}
                </button>
            ),
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
            cell: (item) => (
                <div className="flex space-x-2">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => router.push(`/attribute/view/${item.id}`)}
                        title="View Table"
                    >
                        <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => router.push(`/attribute/update/${item.id}`)}
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
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Attributes</h1>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        Manage attributes with table values.
                    </p>
                </div>
                <Button onClick={() => router.push("/attribute/create")} leftIcon={<Plus className="h-4 w-4" />}>
                    New Attribute
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
                    placeholder="Search attributes..."
                />
            </div>

            {/* Table */}
            <Table
                data={attributes}
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
