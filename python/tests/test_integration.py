import json
import os
from unittest.mock import patch

from opengin.tracer.agents.orchestrator import Agent0


def test_integration_full_pipeline(fs_manager, tmp_path, mock_gemini_response):
    """
    Test the full pipeline flow from Agent 0 to Agent 3 with a mocked LLM.
    Verifies that an input PDF results in an output CSV.
    """
    # Setup inputs
    input_file = tmp_path / "invoice.pdf"
    input_file.touch()
    pipeline_name = "integration_test"
    run_id = "run_full"

    agent0 = Agent0(base_path=str(tmp_path / "pipelines"))

    # We mock:
    # 1. Agent1._split_pdf to return dummy page files
    # 2. extract_data_with_gemini to return valid JSON string

    with (
        patch("opengin.tracer.agents.scanner.Agent1._split_pdf", return_value=[str(tmp_path / "page_1.pdf")]) as _,
        patch(
            "opengin.tracer.agents.scanner.extract_data_with_gemini", return_value=json.dumps(mock_gemini_response)
        ) as _,
    ):

        # 1. Create
        agent0.create_pipeline(pipeline_name, str(input_file), "invoice.pdf", run_id=run_id)

        # 2. Run
        agent0.run_pipeline(pipeline_name, run_id)

        # 3. Verify Output
        output_dir = agent0.fs_manager.get_output_path(pipeline_name, run_id)
        expected_csv = os.path.join(output_dir, "invoice_table.csv")  # "Invoice Table" -> "invoice_table"

        assert os.path.exists(expected_csv)

        with open(expected_csv, "r") as f:
            content = f.read()
            # Check content from mock_gemini_response
            assert "Item,Price" in content
            assert "Widget A,10.00" in content
            assert "Widget B,20.00" in content

        # Verify Metadata Status
        meta = agent0.fs_manager.load_metadata(pipeline_name, run_id)
        assert meta["status"] == "COMPLETED"
