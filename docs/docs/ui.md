# OpenGIN Ingestion UI

This document describes how to install, build, and serve the OpenGIN Ingestion UI.

## File Structure

-   **Frontend**: `python/ui` (Next.js application)
-   **Backend**: `python/src/opengin/server` (FastAPI application)

## Prerequisites

-   **Node.js**: v18 or later.
-   **Python**: v3.11 or later (with `mamba` or `conda` recommended).

## Installation

### 1. Frontend (Next.js)

Navigate to the UI directory and install dependencies:

```bash
cd python/ui
npm install
```

### 2. Backend (FastAPI)

Ensure you have the `doctracer` environment or equivalent set up.

```bash
# If using mamba/conda
mamba activate doctracer
pip install -e ".[tracer]"  # Install opengin with tracer dependencies
pip install uvicorn fastapi python-multipart
```

## Development

To run the application in development mode:

### Backend

```bash
# From the project root
export PYTHONPATH=$PYTHONPATH:python/src
uvicorn opengin.server.main:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at `http://localhost:8001`.

### Frontend

```bash
cd python/ui
npm run dev -- -p 3001 
```

The UI will be available at `http://localhost:3001`.

## Production Build

To build the frontend for production:

```bash
cd python/ui
npm run build
npm start
```

This will run the optimized production server.
