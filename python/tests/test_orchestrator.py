from unittest.mock import patch

import pytest

from opengin.tracer.agents.orchestrator import Agent0


def test_orchestrator_pipeline_flow(fs_manager, tmp_path):
    # Mock sub-agents
    with (
        patch("opengin.tracer.agents.scanner.Agent1") as _,
        patch("opengin.tracer.agents.aggregator.Agent2") as _,
        patch("opengin.tracer.agents.exporter.Agent3") as _,
    ):

        agent0 = Agent0(base_path=str(tmp_path / "pipelines"))

        pipeline_name = "test_pipeline"
        run_id = "run_1"
        input_file = tmp_path / "test.pdf"
        input_file.touch()

        # 1. Create Pipeline
        rid, meta = agent0.create_pipeline(pipeline_name, str(input_file), "test.pdf", run_id=run_id)
        assert rid == run_id
        assert meta["status"] == "READY"

        # 2. Run Pipeline
        agent0.run_pipeline(pipeline_name, run_id)

        # Verify call order
        # Access the return value (instance) of the mocks
        agent0.agent1.run.assert_called_once_with(pipeline_name, run_id, "Extract all tables.")
        agent0.agent2.run.assert_called_once_with(pipeline_name, run_id)
        agent0.agent3.run.assert_called_once_with(pipeline_name, run_id)


def test_orchestrator_failure_handling(fs_manager, tmp_path):
    with patch("opengin.tracer.agents.scanner.Agent1") as _:
        agent0 = Agent0(base_path=str(tmp_path / "pipelines"))

        # Mock Agent1 to raise an exception
        agent0.agent1.run.side_effect = Exception("Simulated Failure")

        pipeline_name = "fail_pipeline"
        run_id = "run_fail"
        fs_manager.initialize_pipeline(pipeline_name, run_id)

        with pytest.raises(Exception) as excinfo:
            agent0.run_pipeline(pipeline_name, run_id)
        assert "Simulated Failure" in str(excinfo.value)

        # Verify status is FAILED
        # Note: We need to use the fs_manager associated with agent0 to check
        meta = agent0.fs_manager.load_metadata(pipeline_name, run_id)
        assert meta["status"] == "FAILED"
        assert "Simulated Failure" in meta["error"]
