/**
 * Application-wide Constants
 * Central place for all constant values used across the application
 */

export * from './entityKinds';
export * from './api';

/**
 * General Application Constants
 */
export const APP_CONFIG = {
    NAME: 'OpenGIN Ingestion',
    VERSION: '0.1.0',
    DEFAULT_PAGE_SIZE: 10,
    MAX_PAGE_SIZE: 100,
} as const;

/**
 * Date/Time Format Constants
 */
export const DATE_FORMATS = {
    DISPLAY: 'MMM dd, yyyy',
    INPUT: 'yyyy-MM-dd',
    DATETIME_INPUT: 'yyyy-MM-dd\'T\'HH:mm',
    ISO: 'yyyy-MM-dd\'T\'HH:mm:ss\'Z\'',
} as const;

/**
 * Validation Constants
 */
export const VALIDATION = {
    MIN_ID_LENGTH: 1,
    MAX_ID_LENGTH: 100,
    MIN_NAME_LENGTH: 1,
    MAX_NAME_LENGTH: 255,
} as const;
