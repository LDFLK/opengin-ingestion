"use client";

import { use, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { useAttribute } from "@/features/attribute/hooks/useAttributes";
import { Pencil, ArrowLeft } from "lucide-react";

export default function ViewAttributePage({ params }: { params: Promise<{ id: string }> }) {
    const router = useRouter();
    const [id, setId] = useState<string>("");

    useEffect(() => {
        params.then((resolvedParams) => {
            setId(resolvedParams.id);
        });
    }, [params]);

    const { data: attribute, isLoading } = useAttribute(id);

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (!attribute) {
        return <div>Attribute not found</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Attribute: {attribute.name}</h1>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        View attribute table value.
                    </p>
                </div>
                <div className="flex space-x-3">
                    <Button variant="secondary" onClick={() => router.back()} leftIcon={<ArrowLeft className="h-4 w-4" />}>
                        Back
                    </Button>
                    <Button onClick={() => router.push(`/attribute/update/${attribute.id}`)} leftIcon={<Pencil className="h-4 w-4" />}>
                        Edit
                    </Button>
                </div>
            </div>

            <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
                <div className="px-4 py-5 sm:px-6">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                        Value Table
                    </h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-800">
                            <tr>
                                {attribute.value.columns.map((col, index) => (
                                    <th key={index} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        {col}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-900 dark:divide-gray-700">
                            {attribute.value.rows.map((row, rowIndex) => (
                                <tr key={rowIndex}>
                                    {attribute.value.columns.map((col) => (
                                        <td key={col} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                            {row[col]}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
