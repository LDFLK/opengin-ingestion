# OpenGIN Ingestion - Documentation

This directory contains documentation for the OpenGIN Ingestion frontend application.

## Documentation Index

- **[API Architecture](./API_ARCHITECTURE.md)** - Explains the Next.js API proxy layer and how READ/INGESTION APIs are separated
- **[API Routes](./ROUTES.md)** - Complete reference for all API routes and endpoints
- **[Constants](../src/constants/README.md)** - Entity kinds, API endpoints, and configuration constants
- **[Testing](./TESTING.md)** - Testing setup and guidelines (coming soon)

## Quick Links

### Architecture
- [API Proxy Architecture](./API_ARCHITECTURE.md#architecture-diagram)
- [Request Flow](./API_ARCHITECTURE.md#request-flow-example)
- [Environment Variables](./API_ARCHITECTURE.md#environment-variables)

### Development
- [Entity Kinds](../src/constants/README.md#entity-kinds)
- [API Endpoints](../src/constants/README.md#api-endpoints)

## Getting Started

1. **Set up environment variables**:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API URLs
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

4. **Run tests**:
   ```bash
   npm test
   ```

## Project Structure

```
prototype/
├── docs/                   # Documentation
├── src/
│   ├── app/
│   │   ├── api/           # Next.js API proxy routes
│   │   └── ...            # Page routes
│   ├── components/        # Shared UI components
│   ├── constants/         # Application constants
│   ├── features/          # Feature modules (entity, relationship, etc.)
│   └── services/          # API service layer
└── .env.example          # Environment variable template
```

## Contributing

When adding new features:
1. Update relevant documentation
2. Add tests for new functionality
3. Follow existing code patterns
4. Update constants if adding new entity kinds or endpoints
