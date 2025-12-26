import pytest


def test_graphql_unique_ids():
    """
    Placeholder for potential future unit tests specifically targeting the resolver logic.
    Currently, the validation of unique ID generation and schema parsing is covered
    by the integration test `test_graphql_extract_mutation_ids`.
    """


@pytest.mark.asyncio
async def test_graphql_extract_mutation_ids(fs_manager, tmp_path, mock_gemini_response):
    from unittest.mock import MagicMock, patch

    from strawberry.file_uploads import Upload

    from opengin.tracer.schema import Mutation

    mutation = Mutation()

    # Mock input file
    upload_file = MagicMock(spec=Upload)
    upload_file.filename = "test.pdf"
    upload_file.file = MagicMock()
    upload_file.file.read.side_effect = [b"fake pdf content", b""]

    # We need to mock Agent0 to return specific data
    with patch("opengin.tracer.agents.orchestrator.Agent0") as MockAgent0:
        agent_instance = MockAgent0.return_value
        # Mock create_pipeline
        run_id = "run_graphql_test"
        agent_instance.create_pipeline.return_value = (run_id, {})

        # Mock fs_manager behavior on the instance
        agent_instance.fs_manager = fs_manager

        # Seed aggregated data
        pipeline_name = "graphql_pipeline"
        fs_manager.initialize_pipeline(pipeline_name, run_id)

        tables = [
            {"name": "Table1", "columns": ["A"], "rows": [["1"]]},
            {"name": "Table1", "columns": ["A"], "rows": [["2"]]},  # Same name
        ]
        fs_manager.save_aggregated_result(pipeline_name, run_id, tables)

        result = await mutation.extract_data(upload_file, "prompt", run_id)

        assert len(result.tables) == 2
        t1 = result.tables[0]
        t2 = result.tables[1]

        # Verify IDs are unique and structured
        assert t1.id == f"{run_id}_0"
        assert t2.id == f"{run_id}_1"
