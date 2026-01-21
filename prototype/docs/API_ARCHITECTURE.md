# API Architecture

## Overview

The OpenGIN Ingestion frontend uses a **Next.js API proxy layer** to communicate with two separate backend APIs:
- **READ API**: For searching and fetching entities
- **INGESTION API**: For creating and updating entities

This architecture solves CORS issues and provides a clean separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (Browser)                                          │
│                                                             │
│  entityService.ts calls:                                    │
│    • fetch('/v1/entities/search') → READ API                │
│    • fetch('/entities') → INGESTION API                     │
│    • fetch('/api/entities/[id]') → READ/INGESTION API       │
└─────────────────┬───────────────────────────────────────────┘
                  │ (same origin, no CORS)
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ NEXT.JS API PROXY ROUTES (Server)                           │
│                                                             │
│  📁 /api/v1/entities/search/route.ts                        │
│    → Forwards to READ_API_URL/v1/entities/search            │
│                                                             │
│  📁 /api/entities/route.ts                                  │
│    → POST forwards to INGESTION_API_URL/entities            │
│                                                             │
│  📁 /api/entities/[id]/route.ts                             │
│    → GET forwards to READ_API_URL/v1/entities/search/{id}   │
│    → PUT forwards to INGESTION_API_URL/entities/{id}        │
└─────────────────┬─────┬─────────────────────────────────────┘
                  │     │
     ┌────────────┘     └────────────┐
     ↓                               ↓
┌──────────────────┐      ┌──────────────────────┐
│ READ API         │      │ INGESTION API        │
│ (port 8080)      │      │ (port 8080)          │
│                  │      │                      │
│ • Search entities│      │ • Create entities    │
│ • Get by ID      │      │ • Update entities    │
└──────────────────┘      └──────────────────────┘
```

## API Routing Table

| Frontend Call | Next.js Proxy Route | HTTP Method | Backend API | Backend Endpoint |
|---------------|---------------------|-------------|-------------|------------------|
| `/v1/entities/search` | `/api/v1/entities/search/route.ts` | POST | **READ** | `/v1/entities/search` |
| `/entities` | `/api/entities/route.ts` | POST | **INGESTION** | `/entities` |
| `/api/entities/[id]` | `/api/entities/[id]/route.ts` | GET | **READ** | `/v1/entities/search/{id}` |
| `/api/entities/[id]` | `/api/entities/[id]/route.ts` | PUT | **INGESTION** | `/entities/{id}` |

## Request Flow Example

### Creating an Entity

```typescript
// 1. Frontend (entityService.ts)
const response = await fetch('/entities', {
  method: 'POST',
  body: JSON.stringify(entity)
});

// 2. Next.js Proxy (/api/entities/route.ts)
const response = await fetch(`${INGESTION_API_URL}/entities`, {
  method: 'POST',
  body: JSON.stringify(body)
});

// 3. INGESTION Backend API
// Receives POST to http://0.0.0.0:8080/entities
```

### Searching Entities by Kind

```typescript
// 1. Frontend (entityService.ts)
const response = await fetch('/v1/entities/search', {
  method: 'POST',
  body: JSON.stringify({ kind: { major: 'Person' } })
});

// 2. Next.js Proxy (/api/v1/entities/search/route.ts)
const response = await fetch(`${READ_API_URL}/v1/entities/search`, {
  method: 'POST',
  body: JSON.stringify(body)
});

// 3. READ Backend API
// Receives POST to http://0.0.0.0:8080/v1/entities/search
```

## Environment Variables

Configure the backend API URLs in `.env.local`:

```bash
# READ API - Used for searching and fetching entities
OPENGIN_READ_API_URL=http://0.0.0.0:8080

# INGESTION API - Used for creating and updating entities
OPENGIN_INGESTION_API_URL=http://0.0.0.0:8080
```

> **Note**: In development, both APIs may point to the same server. In production, they can be separate services.

## Why This Architecture?

### 1. **No CORS Issues**
- Frontend makes same-origin requests to Next.js
- Next.js server makes backend requests (no browser CORS)

### 2. **Security**
- Backend URLs stay on the server (not exposed to browser)
- Can add authentication/authorization at proxy layer

### 3. **Flexibility**
- Easy to switch backend APIs without frontend changes
- Can route to different backends based on environment
- Request/response transformation in one place

### 4. **Clean Separation**
- READ operations clearly separated from WRITE operations
- Different APIs can scale independently

## File Structure

```
src/
├── app/
│   └── api/                    # Next.js API proxy routes
│       ├── v1/
│       │   └── entities/
│       │       └── search/
│       │           └── route.ts  # READ API proxy
│       └── entities/
│           ├── route.ts          # INGESTION API proxy (POST)
│           └── [id]/
│               └── route.ts      # READ (GET) / INGESTION (PUT) proxy
│
├── services/
│   └── entityService.ts        # Frontend service layer
│
└── constants/
    └── api.ts                  # API endpoint constants
```

## Adding New Endpoints

To add a new proxied endpoint:

1. **Create Next.js API route** in `src/app/api/`
2. **Choose correct backend** (READ or INGESTION)
3. **Forward request** to backend
4. **Update frontend service** to call the proxy route

Example:
```typescript
// src/app/api/relationships/route.ts
const INGESTION_API_URL = process.env.OPENGIN_INGESTION_API_URL;

export async function POST(request: NextRequest) {
  const body = await request.json();
  const response = await fetch(`${INGESTION_API_URL}/relationships`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
  return NextResponse.json(await response.json());
}
```

## Testing

All API routes can be tested using Jest. See `src/services/__tests__/entityService.test.ts` for examples.

Mock the `fetch` function to test service layer logic without hitting actual APIs.

## Troubleshooting

### CORS Errors
If you see CORS errors, ensure:
- Frontend is calling Next.js routes (e.g., `/api/entities`), not backend directly
- Environment variables are set correctly

### 404 Errors
- Check Next.js API route exists at the correct path
- Restart dev server after adding new routes
- Verify frontend URL matches proxy route path

### Backend Connection Issues
- Verify backend is running
- Check environment variables in `.env.local`
- Ensure network connectivity to backend
