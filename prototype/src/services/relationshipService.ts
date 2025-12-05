export interface Relationship {
    id: string;
    key: string;
    relatedEntityId: string;
    startTime: string;
    endTime: string;
}

let mockRelationships: Relationship[] = [
    {
        id: "r1",
        key: "REPORTS_TO",
        relatedEntityId: "e2",
        startTime: "2023-01-01T00:00",
        endTime: "",
    },
];

export const relationshipService = {
    getRelationships: async (): Promise<Relationship[]> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        return [...mockRelationships];
    },

    createRelationship: async (relationship: Relationship): Promise<Relationship> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        mockRelationships.push(relationship);
        return relationship;
    },

    getRelationshipById: async (id: string): Promise<Relationship | undefined> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        return mockRelationships.find((r) => r.id === id);
    },

    updateRelationship: async (relationship: Relationship): Promise<Relationship> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        const index = mockRelationships.findIndex((r) => r.id === relationship.id);
        if (index !== -1) {
            mockRelationships[index] = relationship;
            return relationship;
        }
        throw new Error("Relationship not found");
    },
};
