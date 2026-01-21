/**
 * Entity Kind Constants
 * Defines the major and minor kinds for entities in the OpenGIN system
 */

export const ENTITY_KINDS = {
    // Major Kinds
    PERSON: {
        major: 'Person',
        minorKinds: {
            CITIZEN: 'Citizen',
        },
    },
    ORGANIZATION: {
        major: 'Organization',
        minorKinds: {
            GOVERNMENT: 'Government',
            PRIVATE: 'Private',
            NON_PROFIT: 'Non-Profit',
        },
    },
    DATASET: {
        major: 'Dataset',
        minorKinds: {
            TABULAR: 'Tabular',
            DOCUMENT: 'Document',
        },
    },
} as const;

// Helper to get all major kinds as an array
export const MAJOR_KINDS = Object.keys(ENTITY_KINDS).map(
    (key) => ENTITY_KINDS[key as keyof typeof ENTITY_KINDS].major
);

// Helper to get minor kinds for a specific major kind
export function getMinorKinds(majorKind: string): string[] {
    const entry = Object.values(ENTITY_KINDS).find((kind) => kind.major === majorKind);
    return entry ? Object.values(entry.minorKinds) : [];
}

// Type definitions for better TypeScript support
export type MajorKind = typeof ENTITY_KINDS[keyof typeof ENTITY_KINDS]['major'];
export type MinorKind = typeof ENTITY_KINDS[keyof typeof ENTITY_KINDS]['minorKinds'][keyof typeof ENTITY_KINDS[keyof typeof ENTITY_KINDS]['minorKinds']];
