import json
import os
from unittest.mock import patch

from opengin.tracer.agents.aggregator import Agent2
from opengin.tracer.agents.exporter import Agent3
from opengin.tracer.agents.scanner import Agent1


# --- Agent 1 Tests (Scanner) ---
def test_agent1_scanner(fs_manager, mock_gemini_response, tmp_path):
    pipeline_name = "test_pipeline"
    run_id = "run_1"
    fs_manager.initialize_pipeline(pipeline_name, run_id)

    # Create dummy input file
    input_file = tmp_path / "test.pdf"
    input_file.touch()

    # Update metadata with input file path
    meta = fs_manager.load_metadata(pipeline_name, run_id)
    meta["input_file"] = str(input_file)
    fs_manager.save_metadata(pipeline_name, run_id, meta)

    # Mock PDF splitting
    with (
        patch.object(Agent1, "_split_pdf", return_value=[str(tmp_path / "page_1.pdf"), str(tmp_path / "page_2.pdf")]),
        patch(
            "opengin.tracer.agents.scanner.extract_data_with_gemini", return_value=json.dumps(mock_gemini_response)
        ) as _,
    ):

        agent1 = Agent1(fs_manager)
        agent1.run(pipeline_name, run_id, "test prompt")

        # Verify metadata update
        meta = fs_manager.load_metadata(pipeline_name, run_id)
        assert meta["page_count"] == 2

        # Verify intermediate files
        intermediate_files = fs_manager.load_intermediate_results(pipeline_name, run_id)
        assert len(intermediate_files) == 2

        # Check structure
        result = intermediate_files[0]
        assert "message" in result
        assert "raw_response" in result
        assert "tables" in result

        # Verify table content
        extracted_table = result["tables"][0]
        expected_table = mock_gemini_response["tables"][0]
        assert extracted_table["name"] == expected_table["name"]
        assert extracted_table["columns"] == expected_table["columns"]
        assert extracted_table["rows"] == expected_table["rows"]


# --- Agent 2 Tests (Aggregator) ---
def test_agent2_aggregator(fs_manager):
    pipeline_name = "test_pipeline"
    run_id = "run_1"
    fs_manager.initialize_pipeline(pipeline_name, run_id)

    # Seed intermediate results (2 pages, same table name)
    page1_data = {"tables": [{"name": "Invoice", "columns": ["Item", "Cost"], "rows": [["A", "10"]]}]}
    page2_data = {"tables": [{"name": "Invoice", "columns": ["Item", "Cost"], "rows": [["B", "20"]]}]}
    fs_manager.save_intermediate_result(pipeline_name, run_id, 1, page1_data)
    fs_manager.save_intermediate_result(pipeline_name, run_id, 2, page2_data)

    agent2 = Agent2(fs_manager)
    agent2.run(pipeline_name, run_id)

    # Verify aggregated result
    agg_path = fs_manager.get_aggregated_results_path(pipeline_name, run_id)
    assert os.path.exists(agg_path)

    with open(agg_path, "r") as f:
        data = json.load(f)

    assert len(data) == 1
    assert data[0]["name"] == "Invoice"
    assert len(data[0]["rows"]) == 2
    assert data[0]["rows"][0] == ["A", "10"]
    assert data[0]["rows"][1] == ["B", "20"]


# --- Agent 3 Tests (Exporter) ---
def test_agent3_exporter(fs_manager):
    pipeline_name = "test_pipeline"
    run_id = "run_1"
    fs_manager.initialize_pipeline(pipeline_name, run_id)

    # Seed aggregated results
    agg_data = [{"name": "My Table", "columns": ["Col1", "Col2"], "rows": [["Val1", "Val2"]]}]
    fs_manager.save_aggregated_result(pipeline_name, run_id, agg_data)

    agent3 = Agent3(fs_manager)
    agent3.run(pipeline_name, run_id)

    # Verify CSV output
    output_dir = fs_manager.get_output_path(pipeline_name, run_id)
    expected_file = os.path.join(output_dir, "my_table.csv")

    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        content = f.read()
        assert "Col1,Col2" in content
        assert "Val1,Val2" in content

    # Verify status update
    meta = fs_manager.load_metadata(pipeline_name, run_id)
    assert meta["status"] == "COMPLETED"
