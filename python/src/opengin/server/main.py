import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from opengin.server.api import router as api_router

app = FastAPI(title="OpenGIN Ingestion Server", version="0.1.0")

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("opengin.server.main:app", host="0.0.0.0", port=8001, reload=True)
