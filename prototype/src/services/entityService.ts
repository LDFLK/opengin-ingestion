export interface Entity {
    id: string;
    kind: {
        major: string;
        minor: string;
    };
    created: string;
    terminated: string;
    name: {
        value: string;
        startTime: string;
        endTime: string;
    };
    metadata: Array<{ key: string; value: string }>;
    attributes: Array<any>;
    relationships: Array<any>;
}

let mockEntities: Entity[] = [
    {
        id: "e1",
        kind: { major: "example", minor: "test" },
        created: "2024-03-17T10:00:00Z",
        terminated: "",
        name: {
            startTime: "2024-03-17T10:00:00Z",
            endTime: "",
            value: "Sample Entity"
        },
        metadata: [],
        attributes: [],
        relationships: []
    },
];

export const entityService = {
    getEntities: async (): Promise<Entity[]> => {
        try {
            const response = await fetch("/v1/entities");
            if (!response.ok) {
                throw new Error(`Failed to fetch entities: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error("Error fetching entities:", error);
            // Fallback to mock data on error
            return [...mockEntities];
        }
    },

    createEntity: async (entity: Entity): Promise<Entity> => {
        const response = await fetch("/entities", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(entity),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `Failed to create entity: ${response.statusText}`);
        }

        return await response.json();
    },

    getEntityById: async (id: string): Promise<Entity | undefined> => {
        try {
            const response = await fetch(`/v1/entities/search/${id}`);
            if (!response.ok) {
                if (response.status === 404) {
                    return undefined;
                }
                throw new Error(`Failed to fetch entity: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error("Error fetching entity by ID:", error);
            // Fallback to mock data
            return mockEntities.find((e) => e.id === id);
        }
    },

    updateEntity: async (entity: Entity): Promise<Entity> => {
        const response = await fetch(`/api/entities/${entity.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(entity),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `Failed to update entity: ${response.statusText}`);
        }

        return await response.json();
    },
};
