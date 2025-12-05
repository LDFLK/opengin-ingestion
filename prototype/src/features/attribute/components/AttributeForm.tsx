import { useState, useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Attribute, AttributeValue } from "@/services/attributeService";
import { Plus, Trash } from "lucide-react";

interface AttributeFormProps {
    initialData?: Partial<Attribute>;
    onSubmit: (data: Attribute) => void;
    isLoading?: boolean;
    onCancel: () => void;
    submitLabel?: string;
}

export function AttributeForm({ initialData, onSubmit, isLoading, onCancel, submitLabel = "Save" }: AttributeFormProps) {
    const [formData, setFormData] = useState({
        id: "",
        name: "",
        startTime: "",
        endTime: "",
    });

    const [tableValue, setTableValue] = useState<AttributeValue>({
        columns: ["Column 1"],
        rows: [{ "Column 1": "" }],
    });

    useEffect(() => {
        if (initialData) {
            setFormData({
                id: initialData.id || "",
                name: initialData.name || "",
                startTime: initialData.startTime || "",
                endTime: initialData.endTime || "",
            });
            if (initialData.value) {
                setTableValue(initialData.value);
            }
        }
    }, [initialData]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    // Table Editor Handlers
    const addColumn = () => {
        const newColName = `Column ${tableValue.columns.length + 1}`;
        setTableValue((prev) => ({
            ...prev,
            columns: [...prev.columns, newColName],
            rows: prev.rows.map(row => ({ ...row, [newColName]: "" }))
        }));
    };

    const removeColumn = (colIndex: number) => {
        const colName = tableValue.columns[colIndex];
        setTableValue((prev) => {
            const newColumns = prev.columns.filter((_, i) => i !== colIndex);
            const newRows = prev.rows.map(row => {
                const newRow = { ...row };
                delete newRow[colName];
                return newRow;
            });
            return { columns: newColumns, rows: newRows };
        });
    };

    const updateColumnName = (index: number, newName: string) => {
        const oldName = tableValue.columns[index];
        setTableValue((prev) => {
            const newColumns = [...prev.columns];
            newColumns[index] = newName;
            const newRows = prev.rows.map(row => {
                const newRow = { ...row };
                newRow[newName] = newRow[oldName];
                delete newRow[oldName];
                return newRow;
            });
            return { columns: newColumns, rows: newRows };
        });
    };

    const addRow = () => {
        const newRow: Record<string, string> = {};
        tableValue.columns.forEach(col => {
            newRow[col] = "";
        });
        setTableValue((prev) => ({
            ...prev,
            rows: [...prev.rows, newRow]
        }));
    };

    const removeRow = (rowIndex: number) => {
        setTableValue((prev) => ({
            ...prev,
            rows: prev.rows.filter((_, i) => i !== rowIndex)
        }));
    };

    const updateCell = (rowIndex: number, colName: string, value: string) => {
        setTableValue((prev) => {
            const newRows = [...prev.rows];
            newRows[rowIndex] = { ...newRows[rowIndex], [colName]: value };
            return { ...prev, rows: newRows };
        });
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const attribute: Attribute = {
            id: formData.id,
            name: formData.name,
            value: tableValue,
            startTime: formData.startTime,
            endTime: formData.endTime,
        };
        onSubmit(attribute);
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
                <Input
                    label="ID"
                    name="id"
                    id="id"
                    required
                    value={formData.id}
                    onChange={handleInputChange}
                    disabled={!!initialData?.id}
                />
                <Input
                    label="Name"
                    name="name"
                    id="name"
                    required
                    value={formData.name}
                    onChange={handleInputChange}
                />
                <div className="grid grid-cols-2 gap-4">
                    <Input
                        label="Start Time"
                        type="datetime-local"
                        name="startTime"
                        id="startTime"
                        required
                        value={formData.startTime}
                        onChange={handleInputChange}
                    />
                    <Input
                        label="End Time"
                        type="datetime-local"
                        name="endTime"
                        id="endTime"
                        value={formData.endTime}
                        onChange={handleInputChange}
                    />
                </div>
            </div>

            {/* Table Editor */}
            <div className="border rounded-md p-4 space-y-4">
                <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Table Value</h3>
                    <Button type="button" size="sm" onClick={addColumn} leftIcon={<Plus className="h-4 w-4" />}>
                        Add Column
                    </Button>
                </div>

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-800">
                            <tr>
                                {tableValue.columns.map((col, index) => (
                                    <th key={index} className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        <div className="flex items-center space-x-2">
                                            <input
                                                type="text"
                                                value={col}
                                                onChange={(e) => updateColumnName(index, e.target.value)}
                                                className="bg-transparent border-none focus:ring-0 w-full text-xs font-bold"
                                            />
                                            <button type="button" onClick={() => removeColumn(index)} className="text-red-500 hover:text-red-700">
                                                <Trash className="h-3 w-3" />
                                            </button>
                                        </div>
                                    </th>
                                ))}
                                <th className="px-3 py-2 w-10"></th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-900 dark:divide-gray-700">
                            {tableValue.rows.map((row, rowIndex) => (
                                <tr key={rowIndex}>
                                    {tableValue.columns.map((col) => (
                                        <td key={col} className="px-3 py-2 whitespace-nowrap">
                                            <input
                                                type="text"
                                                value={row[col] || ""}
                                                onChange={(e) => updateCell(rowIndex, col, e.target.value)}
                                                className="w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-800 dark:border-gray-700"
                                            />
                                        </td>
                                    ))}
                                    <td className="px-3 py-2 whitespace-nowrap text-right text-sm font-medium">
                                        <button type="button" onClick={() => removeRow(rowIndex)} className="text-red-500 hover:text-red-700">
                                            <Trash className="h-4 w-4" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <Button type="button" size="sm" variant="secondary" onClick={addRow} leftIcon={<Plus className="h-4 w-4" />}>
                    Add Row
                </Button>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
                <Button
                    type="button"
                    variant="secondary"
                    onClick={onCancel}
                    disabled={isLoading}
                >
                    Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                    {isLoading ? "Saving..." : submitLabel}
                </Button>
            </div>
        </form>
    );
}
