import typing
import strawberry
from strawberry.file_uploads import Upload
import shutil
import os
import tempfile
import json
import re

from app.services.gemini import extract_data_with_gemini

@strawberry.type
class Table:
    id: str
    name: str
    columns: typing.List[str]
    rows: typing.List[typing.List[str]]

@strawberry.type
class ExtractionResult:
    message: str
    raw_response: str
    tables: typing.List[Table]

def parse_extraction_response(raw_text: str) -> ExtractionResult:
    """
    Parses the raw text from Gemini which is expected to be a JSON string 
    containing the table structure.
    """
    tables = []
    message = "Extraction complete"
    
    try:
        # Clean up code blocks if present
        json_str = raw_text.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        
        data = json.loads(json_str.strip())
        
        # Expecting data to be a list of tables or a dict with "tables" key
        raw_tables = []
        if isinstance(data, list):
            raw_tables = data
        elif isinstance(data, dict) and "tables" in data:
            raw_tables = data["tables"]
            
        for t in raw_tables:
            tables.append(Table(
                id=str(t.get("id", "")),
                name=t.get("name", "Untitled"),
                columns=t.get("columns", []),
                rows=t.get("rows", [])
            ))
            
    except json.JSONDecodeError:
        message = "Failed to parse JSON response from Gemini"
    except Exception as e:
        message = f"Error processing extracted data: {str(e)}"

    return ExtractionResult(
        message=message,
        raw_response=raw_text,
        tables=tables
    )

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def extract_data(self, file: Upload, prompt: str) -> ExtractionResult:
        # 1. Save uploaded file to temp
        # file.filename and file.file (spooled temp file) are available
        # We need to write it to disk for Gemini upload API to read path (or use stream, but path is safer for MVP)
        
        # Create a temp file with the correct extension to help generic detection
        suffix = ""
        if file.filename:
            _, ext = os.path.splitext(file.filename)
            suffix = ext

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        try:
            # 2. Call Service
            raw_text = extract_data_with_gemini(tmp_path, prompt)
            
            # 3. Parse Response
            return parse_extraction_response(raw_text)
            
        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

schema = strawberry.Schema(query=Query, mutation=Mutation)
