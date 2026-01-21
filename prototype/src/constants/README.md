# Constants Usage Guide

## Overview
Centralized constants for the OpenGIN Ingestion application, providing type-safe access to configuration values, API endpoints, and entity definitions.

## Structure

```
src/constants/
├── index.ts          # Main export file
├── entityKinds.ts    # Entity kind definitions (Major/Minor)
└── api.ts           # API endpoint constants
```

## Entity Kinds

### Usage

```typescript
import { ENTITY_KINDS, MAJOR_KINDS, getMinorKinds } from '@/constants';

// Get all major kinds
const majors = MAJOR_KINDS;  // ['Person', 'Organization', 'Product', ...]

// Access specific kind
const personKind = ENTITY_KINDS.PERSON.major;  // 'Person'
const employeeKind = ENTITY_KINDS.PERSON.minorKinds.EMPLOYEE;  // 'Employee'

// Get minor kinds for a major
const personMinors = getMinorKinds('Person');  // ['Employee', 'Manager', 'Customer', 'Contractor']
```

### Available Major Kinds

- **Person**: Citizen
- **Organization**: Government, Private, Non-Profit
- **Dataset**: Tabular, Document

### Adding New Kinds

Edit `src/constants/entityKinds.ts`:

```typescript
export const ENTITY_KINDS = {
  // ... existing kinds
  NEW_KIND: {
    major: 'NewKind',
    minorKinds: {
      SUB_TYPE_1: 'SubType1',
      SUB_TYPE_2: 'SubType2',
    },
  },
} as const;
```

## API Endpoints

### READ API Endpoints
Used for searching and fetching entities:

```typescript
import { READ_API_ENDPOINTS } from '@/constants';

// Search entities by kind
fetch(READ_API_ENDPOINTS.ENTITIES_SEARCH);  // '/v1/entities/search'
```

### INGESTION API Endpoints
Used for creating and updating entities:

```typescript
import { INGESTION_API_ENDPOINTS } from '@/constants';

// Create entity
fetch(INGESTION_API_ENDPOINTS.ENTITIES);  // '/entities'

// Update entity
fetch(INGESTION_API_ENDPOINTS.ENTITIES_BY_ID('e1'));  // '/entities/e1'
```

### Available Endpoints

**READ API:**
- `ENTITIES_SEARCH`: `/v1/entities/search` (POST with kind payload)

**INGESTION API:**
- `ENTITIES`: `/entities` (POST to create)
- `ENTITIES_BY_ID(id)`: `/entities/{id}` (PUT to update)
- `RELATIONSHIPS`: `/relationships`
- `METADATA`: `/metadata`
- `ATTRIBUTES`: `/attributes`

## General Constants

### App Configuration

```typescript
import { APP_CONFIG } from '@/constants';

console.log(APP_CONFIG.NAME);  // 'OpenGIN Ingestion'
console.log(APP_CONFIG.DEFAULT_PAGE_SIZE);  // 10
```

### Validation

```typescript
import { VALIDATION } from '@/constants';

if (id.length < VALIDATION.MIN_ID_LENGTH) {
  // validation error
}
```

## Best Practices

1. **Always import from `@/constants`** - Don't import from subdirectories
2. **Use constants instead of magic strings** - More maintainable and type-safe
3. **Add new constants to appropriate files** - Keep organization clean
4. **Document new constant groups** - Update this README when adding new sections
