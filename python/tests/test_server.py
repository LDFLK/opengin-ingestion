import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from opengin.server.main import app

client = TestClient(app)


@pytest.fixture
def mock_upload_dir(tmp_path):
    with patch("opengin.server.api.UPLOAD_DIR", str(tmp_path / "uploads")):
        os.makedirs(str(tmp_path / "uploads"), exist_ok=True)
        yield tmp_path / "uploads"


@pytest.fixture
def mock_agent0():
    with patch("opengin.server.api.agent0") as mock:
        yield mock


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_pdf(mock_upload_dir):
    file_content = b"%PDF-1.4 mock content"
    files = {"file": ("test.pdf", file_content, "application/pdf")}

    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "test.pdf"

    # Verify file saved
    saved_path = mock_upload_dir / f"{data['file_id']}.pdf"
    assert saved_path.exists()
    assert saved_path.read_bytes() == file_content


def test_extract_document(mock_upload_dir, mock_agent0):
    # Setup mock file
    file_id = "test-file-id"
    (mock_upload_dir / f"{file_id}.pdf").touch()

    # Mock agent0.create_pipeline
    mock_agent0.create_pipeline.return_value = ("job-123", {"status": "READY"})

    form_data = {"file_id": file_id, "api_key": "test-key", "metadata": "key: value", "prompt": "Extract tables"}

    response = client.post("/api/extract", data=form_data)

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "job-123"
    assert data["status"] == "pending"

    # Verify agent0 calls
    mock_agent0.create_pipeline.assert_called_once()
    # run_pipeline is called in background task. TestClient handles this synchronously.
    mock_agent0.run_pipeline.assert_called_once()
    args, kwargs = mock_agent0.run_pipeline.call_args
    assert kwargs["api_key"] == "test-key"


def test_get_results_success(mock_agent0):
    job_id = "job-123"

    # Mock metadata
    mock_agent0.fs_manager.load_metadata.return_value = {"status": "COMPLETED"}
    mock_agent0.fs_manager.get_pipeline_path.return_value = "/tmp/mock_pipeline/job-123"

    # Mock structure
    with (
        patch("opengin.server.api.os.path.exists", return_value=True),
        patch("opengin.server.api.os.listdir", return_value=["test.csv", "meta.json"]),
        patch("opengin.server.api.os.path.isdir", return_value=False),
    ):

        response = client.get(f"/api/results/{job_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert "files" in data


def test_get_results_not_found(mock_agent0):
    mock_agent0.fs_manager.load_metadata.return_value = {}  # Empty or None

    response = client.get("/api/results/non-existent-job")
    assert response.status_code == 404


def test_get_file_content_forbidden(tmp_path):
    # Attempt to access unrelated file
    # We rely on default base_pipeline_path which mocks won't cover unless we patch it
    # But since we use real_path checks, we can pass an absolute path to /etc/hosts (or equivalent)
    # The default trusted roots are /tmp/opengin_uploads and sandbox/pipelines
    response = client.get("/api/file?path=/etc/passwd")
    assert response.status_code == 403


def test_get_file_content_success(tmp_path):
    # Create a dummy file in a temp directory acting as our pipeline root
    fs_root = tmp_path / "pipelines"
    fs_root.mkdir()
    target_file = fs_root / "output.csv"
    target_file.write_text("col1,col2\nval1,val2")

    # Patch base_pipeline_path in api to point to our temp root
    with patch("opengin.server.api.base_pipeline_path", str(fs_root)):
        response = client.get(f"/api/file?path={str(target_file)}")
        assert response.status_code == 200
        assert response.text == "col1,col2\nval1,val2"


def test_get_file_content_path_traversal(tmp_path):
    # Setup allowed root
    fs_root = tmp_path / "pipelines"
    fs_root.mkdir()

    # Create a secret file OUTSIDE the allowed root
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("secret_data")

    # Attempt to access secret file via traversal relative to allowed root
    # e.g. path = pipelines/../secret.txt
    traversal_path = str(fs_root / "../secret.txt")

    with patch("opengin.server.api.base_pipeline_path", str(fs_root)):
        response = client.get(f"/api/file?path={traversal_path}")
        # Should be forbidden because real path resolves to tmp_path/secret.txt which is not under fs_root
        assert response.status_code == 403


def test_download_all_success(mock_agent0, tmp_path):
    job_id = "job-123"
    run_dir = tmp_path / "sandbox" / "pipelines" / "ui_extraction" / job_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "output.csv").touch()

    mock_agent0.fs_manager.load_metadata.return_value = {"status": "COMPLETED"}
    mock_agent0.fs_manager.get_pipeline_path.return_value = str(run_dir)

    response = client.get(f"/api/download-all/{job_id}")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"


def test_quick_setup_success(mock_upload_dir, tmp_path):
    # Mock the sample file existence
    # We need to mock os.path.exists to return True for one of the search paths
    # AND mock shutil.copy to succeed.

    # We can create a dummy file at one of the expected locations.
    # The API looks at os.getcwd()/../data/quickstart_sample.pdf
    # When running tests, os.getcwd() is python root. ../data is opengin-ingestion/data.

    # Let's mock the search paths or just ensure the file exists in the test env.

    # Using patch for os.path.exists specifically for the sample file check is tricky if we want other checks to work.
    # Instead, let's patch the search logic or creating a temp file and patch os.getcwd? No.

    # Let's use patch("opengin.server.api.os.path.exists") carefully or patch the whole logic.
    # Actually, simpler: create the file at os.getcwd()/../data/quickstart_sample.pdf if we can write there?
    # That pollutes the workspace.

    # Better: Patch `os.getcwd` to return tmp_path, and create `../data` or `data` relative to it.

    fake_root = tmp_path / "fake_root"
    fake_root.mkdir()
    fake_data = fake_root.parent / "data"
    fake_data.mkdir()
    # The API now checks ../data/quickstart_sample.pdf
    (fake_data / "quickstart_sample.pdf").touch()

    with patch("opengin.server.api.os.getcwd", return_value=str(fake_root)):
        response = client.get("/api/quick-setup")

    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["filename"] == "quickstart_sample.pdf"
    assert "metadata" in data
    assert "prompt" in data

    # Verify file copied to upload dir
    saved_path = mock_upload_dir / f"{data['file_id']}.pdf"
    assert saved_path.exists()


def test_quick_setup_not_found(mock_upload_dir):
    # Mock os.path.exists to return False for the sample file paths
    # We wrap the original exists to return False only for pdfs perhaps?
    # Or just ensure the paths don't exist in the test env (which they might if real data is present).
    # Safer to patch os.getcwd to an empty temp dir.

    with patch("opengin.server.api.os.getcwd", return_value="/non/existent/path"):
        response = client.get("/api/quick-setup")

    assert response.status_code == 404
