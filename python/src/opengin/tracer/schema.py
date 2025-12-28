import json
import os
import shutil
import tempfile
import typing

import strawberry
from strawberry.file_uploads import Upload
from strawberry.scalars import JSON


@strawberry.type
class Table:
    """
    Represents a single extracted table.

    Attributes:
        id (str): A unique identifier for the table.
        name (str): The name or title of the table.
        columns (List[str]): Header names for the table columns.
        rows (List[List[str]]): The data rows, where each row is a list of cell values.
        metadata (JSON, optional): Extracted metadata associated with the table.
    """

    id: str
    name: str
    columns: typing.List[str]
    rows: typing.List[typing.List[str]]
    metadata: typing.Optional[JSON] = None


@strawberry.type
class ExtractionResult:
    """
    The result of a data extraction operation.

    Attributes:
        message (str): A status message or error description.
        raw_response (str): The raw text response from the GenAI model (for debugging).
        tables (List[Table]): The list of structured tables extracted from the document.
    """

    message: str
    raw_response: str
    tables: typing.List[Table]


def parse_extraction_response(raw_text: str) -> ExtractionResult:
    """
    Parses the raw JSON response from Gemini into a structured ExtractionResult.

    This function handles:
    1. cleaning markdown code blocks (e.g., ```json ... ```).
    2. parsing the JSON string.
    3. mapping the JSON data to the `Table` and `ExtractionResult` objects.
    4. handling JSON decoding errors.

    Args:
        raw_text (str): The raw string output from the LLM.

    Returns:
        ExtractionResult: The structured result containing tables or error messages.
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
            tables.append(
                Table(
                    id=str(t.get("id", "")),
                    name=t.get("name", "Untitled"),
                    columns=t.get("columns", []),
                    rows=t.get("rows", []),
                    metadata=t.get("metadata", None),
                )
            )

    except json.JSONDecodeError:
        message = "Failed to parse JSON response from Gemini"
    except Exception as e:
        message = f"Error processing extracted data: {str(e)}"

    return ExtractionResult(message=message, raw_response=raw_text, tables=tables)


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def extract_data(self, file: Upload, prompt: str, run_id: typing.Optional[str] = None) -> ExtractionResult:
        """
        GraphQL Mutation to perform data extraction on an uploaded file.

        This mutation integrates with the Agentic Pipeline (Agent0) to process the file.
        It handles:
        1. Saving the uploaded file temporarily.
        2. Initializing and running the Agent0 pipeline.
        3. Retrieving the final aggregated results from the filesystem.
        4. Returning a structured response.

        Args:
            file (Upload): The file to process.
            prompt (str): The extraction instructions.
            run_id (str, optional): A custom ID for the run.

        Returns:
            ExtractionResult: The extracted data and status.
        """
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
            from opengin.tracer.agents.orchestrator import Agent0

            agent0 = Agent0()
            pipeline_name = "graphql_pipeline"

            # Create pipeline (this handles run_id generation if None)
            run_id_val, metadata = agent0.create_pipeline(
                pipeline_name, tmp_path, file.filename or "uploaded.pdf", run_id=run_id
            )

            # Run pipeline
            agent0.run_pipeline(pipeline_name, run_id_val, prompt)

            # 3. Read Aggregated Results
            # We need to construct the result from the aggregated JSON
            fs_manager = agent0.fs_manager
            aggregated_path = fs_manager.get_aggregated_results_path(pipeline_name, run_id_val)

            tables = []
            if os.path.exists(aggregated_path):
                with open(aggregated_path, "r") as f:
                    raw_tables = json.load(f)

                for idx, t in enumerate(raw_tables):
                    # Generate a unique ID using run_id and index
                    unique_id = f"{run_id_val}_{idx}"
                    tables.append(
                        Table(
                            id=unique_id,
                            name=t.get("name", "Untitled"),
                            columns=t.get("columns", []),
                            rows=t.get("rows", []),
                            metadata=t.get("metadata", None),
                        )
                    )

            return ExtractionResult(
                message=f"Pipeline run '{run_id_val}' completed successfully.",
                raw_response="Processed via Agentic Pipeline",
                tables=tables,
            )

        except Exception as e:
            return ExtractionResult(
                message=f"Error processing pipeline: {str(e)}",
                raw_response="",
                tables=[],
            )

        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


schema = strawberry.Schema(query=Query, mutation=Mutation)
