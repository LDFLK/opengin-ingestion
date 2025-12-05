import { useState, useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Metadata } from "@/services/metadataService";

interface MetadataFormProps {
    initialData?: Partial<Metadata>;
    onSubmit: (data: Metadata) => void;
    isLoading?: boolean;
    onCancel: () => void;
    submitLabel?: string;
}

export function MetadataForm({ initialData, onSubmit, isLoading, onCancel, submitLabel = "Save" }: MetadataFormProps) {
    const [formData, setFormData] = useState({
        id: "",
        key: "",
        value: "",
    });

    useEffect(() => {
        if (initialData) {
            setFormData({
                id: initialData.id || "",
                key: initialData.key || "",
                value: initialData.value || "",
            });
        }
    }, [initialData]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const metadata: Metadata = {
            id: formData.id,
            key: formData.key,
            value: formData.value,
        };
        onSubmit(metadata);
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
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
                label="Key"
                name="key"
                id="key"
                required
                value={formData.key}
                onChange={handleInputChange}
            />
            <Input
                label="Value"
                name="value"
                id="value"
                required
                value={formData.value}
                onChange={handleInputChange}
            />
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
