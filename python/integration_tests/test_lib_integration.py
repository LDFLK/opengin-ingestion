import json
import os

from opengin.tracer.agents.orchestrator import Agent0


def run_library_extraction(pdf_path, prompt, metadata_schema, work_dir):
    # Setup
    pipeline_name = "integration_test_lib"
    agent0 = Agent0(base_path=str(work_dir))

    # Create Pipeline
    run_id, metadata = agent0.create_pipeline(pipeline_name, pdf_path, os.path.basename(pdf_path))

    # Run
    agent0.run_pipeline(pipeline_name, run_id, prompt, metadata_schema=metadata_schema)

    # Get Results
    results_path = agent0.fs_manager.get_aggregated_results_path(pipeline_name, run_id)

    if os.path.exists(results_path):
        with open(results_path, "r") as f:
            return json.load(f)
    return None


def test_library_extraction_simple(sample_data_dir, validation_data_dir, metadata_schema, simple_prompt, tmp_path):
    pdf_path = os.path.join(sample_data_dir, "quickstart_sample.pdf")

    # Parse YAML schema from string fixture
    import yaml

    schema = yaml.safe_load(metadata_schema)

    results = run_library_extraction(pdf_path, simple_prompt, schema, tmp_path)

    assert results is not None
    assert len(results) > 0

    # Validation
    golden_file = os.path.join(validation_data_dir, "lib_simple_golden.json")

    if os.environ.get("UPDATE_GOLDEN_DATA") == "1":
        # Mask non-deterministic fields if any (like run_ids in metadata if stored?
        # Agent0 results are usually pure data)
        # But extracted data should be stable.
        with open(golden_file, "w") as f:
            json.dump(results, f, indent=4)

    # Load Golden
    with open(golden_file, "r") as f:
        golden_data = json.load(f)

    # Compare
    # We might need to mask specific dynamic fields if they exist in the output
    # For now, assuming deterministic output for the same model/prompt (mocked or real?)
    # Wait, real extraction uses Gemini. It is NOT deterministic.
    # Integration tests against real LLMs are flaky.
    # User asked to "run it the first time and record them".
    # If the LLM response changes slightly, test fails.
    # We should probably check structural equivalence or key fields, not exact byte match.
    # But for now, let's strictly compare and see.

    # Just check structure for robustness
    assert len(results) == len(golden_data)
    assert results[0].keys() == golden_data[0].keys()
