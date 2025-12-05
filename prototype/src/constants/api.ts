/**
 * API Endpoints Constants
 */

// READ API - Used for searching and fetching entities
export const READ_API_ENDPOINTS = {
    ENTITIES_SEARCH: '/v1/entities/search',
} as const;

// INGESTION API - Used for creating and updating entities
export const INGESTION_API_ENDPOINTS = {
    ENTITIES: '/entities',
    ENTITIES_BY_ID: (id: string) => `/entities/${id}`,
    RELATIONSHIPS: '/relationships',
    METADATA: '/metadata',
    ATTRIBUTES: '/attributes',
} as const;

/**
 * API Configuration
 */
export const API_CONFIG = {
    TIMEOUT: 30000, // 30 seconds
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000, // 1 second
} as const;
