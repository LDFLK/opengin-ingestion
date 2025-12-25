from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.schema import schema

app = FastAPI()

graphql_app = GraphQLRouter(schema, multipart_uploads_enabled=True)

app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def read_root():
    return {"message": "Welcome to Document Data Extraction API. Go to /graphql to use the tool."}
