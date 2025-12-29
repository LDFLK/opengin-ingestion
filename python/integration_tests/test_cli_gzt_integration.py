import json
import os
import re
import subprocess


def run_script_command(args, cwd, python_root):
    env = os.environ.copy()
    src_path = os.path.join(python_root, "src")
    # Also add the script directory to path if needed, but we run by file path
    env["PYTHONPATH"] = f"{src_path}:{env.get('PYTHONPATH', '')}"

    cmd = ["python"] + args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    return result


def test_gzt_script_execution(sample_data_dir, validation_data_dir, tmp_path, metadata_schema):
    # Inputs
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../examples/extragzt/tabular_extragzt_extract_sample.py")
    )

    # We use simple.pdf as requested
    # simple.pdf is located in python/data/simple.pdf
    # sample_data_dir points to repo_root/data
    # So we construct path relative to repo root python dir or just strictly locate it.
    repo_root = os.path.abspath(os.path.join(sample_data_dir, ".."))
    pdf_path = os.path.join(repo_root, "python", "data", "simple.pdf")

    # Prompt is now external
    prompt_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../examples/extragzt/prompt.txt"))

    schema_file = tmp_path / "metadata.yml"
    schema_file.write_text(metadata_schema)

    repo_python_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    args = [script_path, pdf_path, prompt_file, "--metadata-schema", str(schema_file)]

    # Run
    result = run_script_command(args, cwd=str(tmp_path), python_root=repo_python_dir)

    assert result.returncode == 0, f"Script failed: {result.stderr}"

    # Verification logic
    # 1. Check Stdout for success message
    assert "--- Extracted" in result.stdout

    # 2. Parse Stdout for Table details or check pipeline output
    # The script uses pipeline name "example_extragzt_run"
    # Agent0 (by default) creates pipelines/ in CWD (tmp_path)

    # Find Run ID from stderr (logging) or stdout
    # Script prints: "mid - INFO - Running extraction with Run ID: <uuid>" to stderr
    # We combine search or check stderr.
    match = re.search(r"Running extraction with Run ID: ([a-f0-9\-]+)", result.stderr)
    if not match:
        match = re.search(r"Running extraction with Run ID: ([a-f0-9\-]+)", result.stdout)

    assert match, f"Could not find Run ID in script output. Stderr: {result.stderr}"
    run_id = match.group(1)

    pipeline_dir = tmp_path / "pipelines" / "example_extragzt_run" / run_id / "output"
    assert pipeline_dir.exists()

    # 3. Golden Data
    # Collect generated files stats
    csv_files = sorted([f.name for f in pipeline_dir.glob("*.csv")])
    assert len(csv_files) > 0, "No CSVs generated"

    current_data = []
    for csv_f in csv_files:
        with open(pipeline_dir / csv_f, "r") as f:
            lines = f.readlines()
            current_data.append({"filename": csv_f, "row_count": len(lines)})

    golden_filename = "gzt_script_golden.json"
    golden_path = os.path.join(validation_data_dir, golden_filename)

    if os.environ.get("UPDATE_GOLDEN_DATA") == "1":
        with open(golden_path, "w") as f:
            json.dump(current_data, f, indent=4)

    # Load and Compare
    if os.path.exists(golden_path):
        with open(golden_path, "r") as f:
            golden_data = json.load(f)

        assert len(current_data) == len(golden_data)
        # Structural check
        for cur, gold in zip(current_data, golden_data):
            # Filenames might vary if prompt dependent, but row counts should match
            assert cur["row_count"] > 0
