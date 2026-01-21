import { useState, useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Relationship } from "@/services/relationshipService";

interface RelationshipFormProps {
    initialData?: Partial<Relationship>;
    onSubmit: (data: Relationship) => void;
    isLoading?: boolean;
    onCancel: () => void;
    submitLabel?: string;
}

export function RelationshipForm({ initialData, onSubmit, isLoading, onCancel, submitLabel = "Save" }: RelationshipFormProps) {
    const [formData, setFormData] = useState({
        id: "",
        key: "",
        relatedEntityId: "",
        startTime: "",
        endTime: "",
    });

    useEffect(() => {
        if (initialData) {
            setFormData({
                id: initialData.id || "",
                key: initialData.key || "",
                relatedEntityId: initialData.relatedEntityId || "",
                startTime: initialData.startTime || "",
                endTime: initialData.endTime || "",
            });
        }
    }, [initialData]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const relationship: Relationship = {
            id: formData.id,
            key: formData.key,
            relatedEntityId: formData.relatedEntityId,
            startTime: formData.startTime,
            endTime: formData.endTime,
        };
        onSubmit(relationship);
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
                label="Relationship Key"
                name="key"
                id="key"
                required
                value={formData.key}
                onChange={handleInputChange}
            />
            <Input
                label="Related Entity ID"
                name="relatedEntityId"
                id="relatedEntityId"
                required
                value={formData.relatedEntityId}
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
