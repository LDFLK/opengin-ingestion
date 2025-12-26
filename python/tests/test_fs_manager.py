import os


def test_pipeline_initialization(fs_manager, temp_pipeline_dir):
    pipeline_name = "test_pipeline"
    run_id = "run_123"

    fs_manager.initialize_pipeline(pipeline_name, run_id)

    base_path = os.path.join(temp_pipeline_dir, pipeline_name, run_id)
    assert os.path.exists(os.path.join(base_path, "input"))
    assert os.path.exists(os.path.join(base_path, "intermediate"))
    assert os.path.exists(os.path.join(base_path, "aggregated"))
    assert os.path.exists(os.path.join(base_path, "output"))
    assert os.path.exists(os.path.join(base_path, "metadata.json"))


def test_metadata_operations(fs_manager):
    pipeline_name = "test_pipeline"
    run_id = "run_123"
    fs_manager.initialize_pipeline(pipeline_name, run_id)

    # Check initial metadata
    meta = fs_manager.load_metadata(pipeline_name, run_id)
    assert meta["status"] == "INITIALIZED"
    assert meta["page_count"] == 0

    # Update metadata
    meta["status"] = "Running"
    fs_manager.save_metadata(pipeline_name, run_id, meta)

    loaded_meta = fs_manager.load_metadata(pipeline_name, run_id)
    assert loaded_meta["status"] == "Running"


def test_list_and_delete_operations(fs_manager):
    pipeline_name = "test_pipeline"
    run_id_1 = "run_1"
    run_id_2 = "run_2"

    fs_manager.initialize_pipeline(pipeline_name, run_id_1)
    fs_manager.initialize_pipeline(pipeline_name, run_id_2)

    # List pipelines
    pipelines = fs_manager.list_pipelines()
    assert pipeline_name in pipelines

    # List runs
    runs = fs_manager.list_runs(pipeline_name)
    assert run_id_1 in runs
    assert run_id_2 in runs

    # Delete run
    assert fs_manager.delete_run(pipeline_name, run_id_1)
    runs_after = fs_manager.list_runs(pipeline_name)
    assert run_id_1 not in runs_after
    assert run_id_2 in runs_after

    # Delete pipeline
    assert fs_manager.delete_pipeline(pipeline_name)
    pipelines_after = fs_manager.list_pipelines()
    assert pipeline_name not in pipelines_after


def test_path_helpers(fs_manager, temp_pipeline_dir):
    pipeline_name = "p1"
    run_id = "r1"

    expected_output = os.path.join(temp_pipeline_dir, pipeline_name, run_id, "output")
    assert fs_manager.get_output_path(pipeline_name, run_id) == expected_output

    expected_pages = os.path.join(temp_pipeline_dir, pipeline_name, run_id, "input", "pages")
    assert fs_manager.get_input_pages_dir(pipeline_name, run_id) == expected_pages
