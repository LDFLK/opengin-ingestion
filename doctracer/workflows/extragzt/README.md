# Tabular ExtraGZT Extraction Sample

This workflow demonstrates how to use the Doctracer API to extract structured tabular data from PDF documents, specifically tailored for minister schedule documents (as defined in the `tabular_extragzt_extract_sample.py` prompt).

## Prerequisites

- The Doctracer API server must be running (default: `http://localhost:8000`).
- Python 3+ and `requests` library installed.

## Usage

Run the sample script by providing the path to your PDF document:

```bash
python tabular_extragzt_extract_sample.py data/simple.pdf
```

### Options

- `file_path`: (Required) Path to the target PDF file.
- `--url`: (Optional) URL of the GraphQL API endpoint. Default is `http://localhost:8000/graphql`.

Example with custom URL:
```bash
python tabular_extragzt_extract_sample.py my_document.pdf --url http://api.example.com/graphql
```

## Logic
The script:
1.  Constructs a GraphQL `uploadAndExtract` mutation.
2.  Sends a multipart POST request with the PDF file and a specialized prompt.
3.  Parses the JSON response to display extracted table metadata.
