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


def test_agent3_exporter_collision(fs_manager):
    pipeline_name = "test_pipeline"
    run_id = "run_collision"
    fs_manager.initialize_pipeline(pipeline_name, run_id)

    # Seed aggregated results with duplicate names
    agg_data = [
        {"name": "My Table", "columns": ["C1"], "rows": [["V1"]]},
        {"name": "My Table", "columns": ["C1"], "rows": [["V2"]]},
        {"name": "My_Table", "columns": ["C1"], "rows": [["V3"]]},  # Should also conflict
    ]
    fs_manager.save_aggregated_result(pipeline_name, run_id, agg_data)

    agent3 = Agent3(fs_manager)
    agent3.run(pipeline_name, run_id)

    output_dir = fs_manager.get_output_path(pipeline_name, run_id)

    # We expect my_table.csv, my_table_1.csv, my_table_2.csv
    files = sorted(os.listdir(output_dir))
    csv_files = [f for f in files if f.endswith(".csv")]

    assert len(csv_files) == 3
    assert "my_table.csv" in csv_files
    assert "my_table_1.csv" in csv_files
    assert "my_table_2.csv" in csv_files


def test_agent2_aggregator_schema_mismatch(fs_manager):
    pipeline_name = "test_pipeline"
    run_id = "run_schema_mismatch"
    fs_manager.initialize_pipeline(pipeline_name, run_id)

    # Seed intermediate results with same table name but different schemas
    page1_data = {"tables": [{"name": "Sales", "columns": ["Item", "Price"], "rows": [["Apple", "1.0"]]}]}
    # Page 2 has an extra column "Qty"
    page2_data = {"tables": [{"name": "Sales", "columns": ["Item", "Price", "Qty"], "rows": [["Banana", "0.5", "10"]]}]}
    # Page 3 matches Page 1
    page3_data = {"tables": [{"name": "Sales", "columns": ["Item", "Price"], "rows": [["Cherry", "2.0"]]}]}

    fs_manager.save_intermediate_result(pipeline_name, run_id, 1, page1_data)
    fs_manager.save_intermediate_result(pipeline_name, run_id, 2, page2_data)
    fs_manager.save_intermediate_result(pipeline_name, run_id, 3, page3_data)

    agent2 = Agent2(fs_manager)
    agent2.run(pipeline_name, run_id)

    # Verify results
    agg_path = fs_manager.get_aggregated_results_path(pipeline_name, run_id)

    with open(agg_path, "r") as f:
        data = json.load(f)

    # We expect 2 separate tables:
    # 1. "Sales" with 2 rows (Apple, Cherry)
    # 2. "Sales (1)" (or variant name) with 1 row (Banana)

    assert len(data) == 2

    # Convert to a dict key map for easier checking
    tables_map = {t["name"]: t for t in data}

    # Check Schema 1
    assert "Sales" in tables_map
    t1 = tables_map["Sales"]
    assert t1["columns"] == ["Item", "Price"]
    assert len(t1["rows"]) == 2
    assert t1["rows"][0][0] == "Apple"
    assert t1["rows"][1][0] == "Cherry"

    # Check Schema 2
    # The name logic I added uses "orig_name (1)" for the first variant if counter was 2
    # But wait, logic was: "name": orig_name if counter == 1 else f"{orig_name} ({counter-1})"
    # If mismatch, counter increments to 2. Key becomes name_2.
    # Name becomes "Sales (1)".
    variant_name = "Sales (1)"
    assert variant_name in tables_map
    t2 = tables_map[variant_name]
    assert t2["columns"] == ["Item", "Price", "Qty"]
    assert len(t2["rows"]) == 1
    assert t2["rows"][0][0] == "Banana"
