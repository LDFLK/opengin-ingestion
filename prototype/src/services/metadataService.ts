export interface Metadata {
    id: string;
    key: string;
    value: string;
}

let mockMetadata: Metadata[] = [
    { id: "m1", key: "source", value: "HR System" },
    { id: "m2", key: "version", value: "1.0" },
];

export const metadataService = {
    getMetadata: async (): Promise<Metadata[]> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        return [...mockMetadata];
    },

    createMetadata: async (metadata: Metadata): Promise<Metadata> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        mockMetadata.push(metadata);
        return metadata;
    },

    getMetadataById: async (id: string): Promise<Metadata | undefined> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        return mockMetadata.find((m) => m.id === id);
    },

    updateMetadata: async (metadata: Metadata): Promise<Metadata> => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        const index = mockMetadata.findIndex((m) => m.id === metadata.id);
        if (index !== -1) {
            mockMetadata[index] = metadata;
            return metadata;
        }
        throw new Error("Metadata not found");
    },
};
