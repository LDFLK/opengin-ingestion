# Document Data Extraction MVP

This project is a Document Data Extraction tool powered by Google Gemini 2.0 Flash (via Google Files API). It exposes a GraphQL API to upload documents and extract structured metadata, tables, and statistics.

## Prerequisites

- Python 3.10+
- A Google Gemini API Key

## Setup

1.  **Clone the repository** (if applicable)
2.  **Create and activate a virtual environment**:
    ```bash
    mamba create -n doctracer python=3.10 -y
    mamba activate doctracer
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Environment Variables**:
    Export your API key:
    ```bash
    export GOOGLE_API_KEY="your_api_key_here"
    ```

## Running the Server

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

## Usage

Visit `http://localhost:8000/graphql` to access the GraphiQL interface.

**Example Mutation:**
```graphql
mutation UploadAndExtract($file: Upload!, $prompt: String!) {
  extractData(file: $file, prompt: $prompt) {
    message
    rawResponse
    tables {
      id
      name
      columns
      rows
    }
  }
}
```

## Pipeline Management CLI

A dedicated CLI tool is available to manage pipeline runs, debug issues, and clean up old data.

### Commands

**List Runs**
View all pipeline runs and their status:
```bash
python app/cli.py list-runs
```

**Run Info**
Get detailed information about a specific run, including generated output files:
```bash
python app/cli.py info <pipeline_name> <run_id>
```

**Delete Run**
Delete a run and its associated data:
```bash
python app/cli.py delete <pipeline_name> <run_id>
```
