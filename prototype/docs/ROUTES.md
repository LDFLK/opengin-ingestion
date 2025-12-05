# API Routes Reference

This document provides a comprehensive reference for all API routes in the OpenGIN Ingestion frontend.

## Route Flow

```
Frontend Service → Next.js API Proxy → Backend API
```

## Complete Routes Table

| Operation | Frontend URL | Next.js Route File | HTTP Method | Backend API | Backend URL |
|-----------|--------------|-------------------|-------------|-------------|-------------|
| **Search entities by kind** | `/api/v1/entities/search` | `api/v1/entities/search/route.ts` | POST | READ | `/v1/entities/search` |
| **Create entity** | `/api/entities` | `api/entities/route.ts` | POST | INGESTION | `/entities` |
| **Get entity by ID** | `/api/v1/entities/search/{id}` | `api/v1/entities/search/route.ts` | GET | READ | `/v1/entities/search/{id}` |
| **Update entity** | `/api/entities/{id}` | `api/entities/[id]/route.ts` | PUT | INGESTION | `/entities/{id}` |
| **List all entities** | `/api/entities` | `api/entities/route.ts` | GET | READ | `/entities` ⚠️ |

⚠️ **Note**: The "List all entities" endpoint is not yet implemented in OpenGIN backend.

## Route Details

### Search Entities by Kind

**Purpose**: Search for entities by major kind (Person, Organization, Dataset)

```typescript
// Frontend (entityService.ts)
const response = await fetch('/api/v1/entities/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    kind: { major: 'Person' }
  })
});
```

- **Frontend URL**: `/api/v1/entities/search`
- **Proxy File**: `src/app/api/v1/entities/search/route.ts`
- **Backend**: READ API → `/v1/entities/search`
- **Method**: POST
- **Payload**: `{ kind: { major: string } }`
- **Returns**: Array of entities

---

### Create Entity

**Purpose**: Create a new entity in the system

```typescript
// Frontend (entityService.ts)
const response = await fetch('/api/entities', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(entity)
});
```

- **Frontend URL**: `/api/entities`
- **Proxy File**: `src/app/api/entities/route.ts`
- **Backend**: INGESTION API → `/entities`
- **Method**: POST
- **Payload**: Entity object
- **Returns**: Created entity

---

### Get Entity by ID

**Purpose**: Fetch a single entity by its ID

```typescript
// Frontend (entityService.ts)
const response = await fetch(`/api/v1/entities/search/${id}`);
```

- **Frontend URL**: `/api/v1/entities/search/{id}`
- **Proxy File**: `src/app/api/v1/entities/search/route.ts` (needs to support ID param)
- **Backend**: READ API → `/v1/entities/search/{id}`
- **Method**: GET
- **Returns**: Single entity or 404

---

### Update Entity

**Purpose**: Update an existing entity

```typescript
// Frontend (entityService.ts)
const response = await fetch(`/api/entities/${entity.id}`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(entity)
});
```

- **Frontend URL**: `/api/entities/{id}`
- **Proxy File**: `src/app/api/entities/[id]/route.ts`
- **Backend**: INGESTION API → `/entities/{id}`
- **Method**: PUT
- **Payload**: Updated entity object
- **Returns**: Updated entity

---

## File Locations

```
src/app/api/
├── v1/
│   └── entities/
│       └── search/
│           └── route.ts          # Search entities by kind
│
└── entities/
    ├── route.ts                  # Create entity (POST)
    └── [id]/
        └── route.ts             # Get (GET) / Update (PUT) entity
```

## Frontend Service Mapping

All route calls originate from `src/services/entityService.ts`:

```typescript
export const entityService = {
  getEntities: () => fetch('/api/v1/entities/search', ...),  // Search by kind
  createEntity: () => fetch('/api/entities', ...),           // Create
  getEntityById: () => fetch('/api/v1/entities/search/{id}'),// Get by ID
  updateEntity: () => fetch('/api/entities/{id}', ...),      // Update
}
```

## Adding New Routes

To add a new route:

1. **Create Next.js API route** in `src/app/api/`
   ```typescript
   // src/app/api/my-endpoint/route.ts
   export async function POST(request: NextRequest) {
     const body = await request.json();
     const response = await fetch(`${BACKEND_URL}/my-endpoint`, {
       method: 'POST',
       body: JSON.stringify(body),
     });
     return NextResponse.json(await response.json());
   }
   ```

2. **Update frontend service** to call the new route
   ```typescript
   // src/services/myService.ts
   const response = await fetch('/api/my-endpoint', { ... });
   ```

3. **Update this documentation** with the new route

## Environment Configuration

Routes use environment variables to determine backend URLs:

```bash
# .env.local
OPENGIN_READ_API_URL=http://0.0.0.0:8080
OPENGIN_INGESTION_API_URL=http://0.0.0.0:8080
```

## Testing Routes

Routes can be tested using:

1. **Unit Tests**: Mock `fetch` in service tests
2. **Integration Tests**: Test Next.js API routes directly
3. **Manual Testing**: Use browser DevTools Network tab

```typescript
// Example service test
global.fetch = jest.fn();

(fetch as jest.Mock).mockResolvedValueOnce({
  ok: true,
  json: async () => ({ id: 'e1' })
});

const result = await entityService.getEntityById('e1');
expect(fetch).toHaveBeenCalledWith('/api/v1/entities/search/e1');
```

## Common Issues

### 404 Not Found
- ✅ Ensure frontend URL starts with `/api/`
- ✅ Check Next.js route file exists
- ✅ Restart dev server after adding new routes

### CORS Errors
- ✅ All requests should go through `/api/` routes
- ✅ Never call backend URLs directly from frontend

### Wrong Backend API
- ✅ Check proxy route uses correct `READ_API_URL` or `INGESTION_API_URL`
- ✅ Verify environment variables are set
