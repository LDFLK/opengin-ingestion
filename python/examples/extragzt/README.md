# Tabular Data Extraction Example

This example demonstrates how to use the `opengin.tracer` library to extract tabular data from PDF documents using the agentic pipeline.

## Prerequisites

Ensure you have the `opengin` package installed in your environment. If you are running from the source root:

```bash
pip install -e .
```

## Usage

Run the example script by providing the path to a PDF file you want to process.

```bash
python examples/extragzt/tabular_extragzt_extract_sample.py <path_to_pdf>
```

### Example

To run the extraction on the provided sample data:

```bash
python examples/extragzt/tabular_extragzt_extract_sample.py data/simple.pdf
```

## Output

The script will:
1. Initialize an extraction pipeline.
2. Upload the PDF pages to Gemini for processing.
3. Extract tables based on the predefined prompt.
4. Aggregate the results.
5. Print the summary of extracted tables to the console.
6. Export CSV files to the `pipelines/example_extragzt_run/<run_id>/output/` directory.
