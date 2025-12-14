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
    async def extract_data(self, file: Upload, prompt: str, runId: typing.Optional[str] = None) -> ExtractionResult:
        # 1. Save uploaded file to temp
        suffix = ""
        if file.filename:
            _, ext = os.path.splitext(file.filename)
            suffix = ext

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        try:
            # 2. Use Agent0 Orchestrator
            from app.agents.orchestrator import Agent0
            agent0 = Agent0()
            pipeline_name = "graphql_pipeline"
            
            # Create pipeline (this handles run_id generation if None)
            run_id, metadata = agent0.create_pipeline(pipeline_name, tmp_path, file.filename or "uploaded.pdf", run_id=runId)
            
            # Run pipeline
            agent0.run_pipeline(pipeline_name, run_id, prompt)
            
            # 3. Read Aggregated Results
            # We need to construct the result from the aggregated JSON
            fs_manager = agent0.fs_manager
            aggregated_path = os.path.join(fs_manager._get_pipeline_path(pipeline_name, run_id), "aggregated", "tables.json")
            
            tables = []
            if os.path.exists(aggregated_path):
                with open(aggregated_path, "r") as f:
                    raw_tables = json.load(f)
                    
                import csv
                import io

                for t in raw_tables:
                    csv_content = t.get("csv", "")
                    columns = []
                    rows = []
                    
                    if csv_content:
                        f = io.StringIO(csv_content)
                        reader = csv.reader(f)
                        try:
                            headers = next(reader)
                            columns = headers
                            rows = list(reader)
                        except StopIteration:
                            pass
                            
                    tables.append(Table(
                        id=str(t.get("name", "table_id")), # Use name as ID for now or generate UUID
                        name=t.get("name", "Untitled"),
                        columns=columns,
                        rows=rows
                    ))
            
            return ExtractionResult(
                message=f"Pipeline run '{run_id}' completed successfully.",
                raw_response="Processed via Agentic Pipeline",
                tables=tables
            )
            
        except Exception as e:
            return ExtractionResult(
                message=f"Error processing pipeline: {str(e)}",
                raw_response="",
                tables=[]
            )
            
        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

schema = strawberry.Schema(query=Query, mutation=Mutation)
