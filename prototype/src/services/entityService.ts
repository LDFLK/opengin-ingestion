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
            // Import major kinds from constants
            const { MAJOR_KINDS } = await import('@/constants');

            // Query each major kind separately using POST with JSON payload
            const searchPromises = MAJOR_KINDS.map(async (majorKind) => {
                try {
                    const response = await fetch('/api/v1/entities/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            kind: {
                                major: majorKind
                            }
                        }),
                    });

                    // 404 means no entities of this kind exist - this is normal, not an error
                    if (response.status === 404) {
                        return [];
                    }

                    // Log actual errors (5xx, network issues, etc.)
                    if (!response.ok) {
                        console.error(`Failed to fetch entities for kind ${majorKind}:`, response.status, response.statusText);
                        return [];
                    }

                    const data = await response.json();
                    // Assuming the API returns an array or object with entities array
                    return Array.isArray(data) ? data : (data.entities || []);
                } catch (error) {
                    console.error(`Error fetching entities for kind ${majorKind}:`, error);
                    return [];
                }
            });

            // Wait for all searches to complete
            const results = await Promise.all(searchPromises);

            // Flatten and aggregate all results
            const allEntities = results.flat();

            return allEntities;
        } catch (error) {
            console.error("Error fetching entities:", error);
            // Fallback to mock data on error
            return [...mockEntities];
        }
    },

    createEntity: async (entity: Entity): Promise<Entity> => {
        const response = await fetch("/api/entities", {
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
            // Search by ID using POST with ID in payload
            const response = await fetch('/api/v1/entities/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: id
                }),
            });

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
