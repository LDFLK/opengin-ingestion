import { useState, useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Entity } from "@/services/entityService";

interface EntityFormProps {
    initialData?: Partial<Entity>;
    onSubmit: (data: Entity) => void;
    isLoading?: boolean;
    onCancel: () => void;
    submitLabel?: string;
}

export function EntityForm({ initialData, onSubmit, isLoading, onCancel, submitLabel = "Save" }: EntityFormProps) {
    const [formData, setFormData] = useState({
        id: "",
        majorKind: "",
        minorKind: "",
        name: "",
        startTime: "",
        endTime: "",
    });

    // Helper to format ISO string (UTC) to local datetime string for input (yyyy-MM-ddThh:mm)
    const formatToLocalInput = (isoString?: string) => {
        if (!isoString) return "";
        try {
            const date = new Date(isoString);
            const localDate = new Date(date.getTime());
            return localDate.toISOString().slice(0, 16);
        } catch (e) {
            console.error("Invalid date string:", isoString);
            return "";
        }
    };

    // Helper to format local datetime string from input back to ISO string (UTC) with Z
    const formatToUTC = (localString: string) => {
        if (!localString) return "";
        try {
            const date = new Date(localString);
            return date.toISOString();
        } catch (e) {
            console.error("Invalid local date string:", localString);
            return "";
        }
    };

    useEffect(() => {
        if (initialData) {
            setFormData({
                id: initialData.id || "",
                majorKind: initialData.kind?.major || "",
                minorKind: initialData.kind?.minor || "",
                name: initialData.name?.value || "",
                startTime: formatToLocalInput(initialData.created),
                endTime: formatToLocalInput(initialData.terminated),
            });
        }
    }, [initialData]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        // Auto-generate created timestamp if not present (for new entities)
        const now = new Date().toISOString();

        const entity: Entity = {
            id: formData.id,
            kind: {
                major: formData.majorKind,
                minor: formData.minorKind,
            },
            // Prefer existing created time (re-converted to UTC if edited via startTime inputs) 
            // OR use formatted startTime from form 
            // OR default to now
            created: formData.startTime ? formatToUTC(formData.startTime) : (initialData?.created || now),

            terminated: formData.endTime ? formatToUTC(formData.endTime) : (initialData?.terminated || ""),

            name: {
                value: formData.name,
                startTime: formData.startTime ? formatToUTC(formData.startTime) : (initialData?.name?.startTime || now),
                endTime: formData.endTime ? formatToUTC(formData.endTime) : (initialData?.name?.endTime || ""),
            },
            metadata: initialData?.metadata || [],
            attributes: initialData?.attributes || [],
            relationships: initialData?.relationships || [],
        };
        onSubmit(entity);
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
                disabled={!!initialData?.id} // Disable ID editing for updates if desired
            />
            <div className="grid grid-cols-2 gap-4">
                <Input
                    label="Major Kind"
                    name="majorKind"
                    id="majorKind"
                    required
                    value={formData.majorKind}
                    onChange={handleInputChange}
                    disabled={!!initialData?.id} // Disable Kind editing for updates
                />
                <Input
                    label="Minor Kind"
                    name="minorKind"
                    id="minorKind"
                    required
                    value={formData.minorKind}
                    onChange={handleInputChange}
                    disabled={!!initialData?.id} // Disable Kind editing for updates
                />
            </div>
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
