import os
import shutil
import tempfile

from fastapi import FastAPI
from fastapi.testclient import TestClient

from opengin.server.api import UPLOAD_DIR, is_safe_path, router

# Create a clean app for testing just the router if needed,
# or assume we can test functions directly or via dependency override.
# For simplicity, let's test the helper and the endpoint.

app = FastAPI()
app.include_router(router, prefix="/api")

client = TestClient(app)


def test_is_safe_path():
    with tempfile.TemporaryDirectory() as base_dir:
        # Create a file inside
        safe_file = os.path.join(base_dir, "safe.txt")
        with open(safe_file, "w") as f:
            f.write("content")

        # Create a file outside
        outside_dir = tempfile.mkdtemp()
        outside_file = os.path.join(outside_dir, "unsafe.txt")
        with open(outside_file, "w") as f:
            f.write("secret")

        try:
            # Case 1: Direct child
            assert is_safe_path(base_dir, safe_file) is True

            # Case 2: Outside file
            assert is_safe_path(base_dir, outside_file) is False

            # Case 3: Traversal attack to outside
            # base/../outside/unsafe.txt -> resolves to outside_file
            traversal_path = os.path.join(base_dir, "..", os.path.basename(outside_dir), "unsafe.txt")
            assert is_safe_path(base_dir, traversal_path) is False

            # Case 4: Non-existent file inside (should still be "safe path" conceptually,
            # though get_file_content checks existence separately)
            # os.path.realpath resolves non-existent paths by appending to cwd or resolving logically?
            # actually strict realpath might fail if components don't exist on some OS, but on unix it resolves as much as possible.
            # safe_path just checks if if fully resolved path starts with base.
            missing_safe = os.path.join(base_dir, "missing.txt")
            assert is_safe_path(base_dir, missing_safe) is True

        finally:
            shutil.rmtree(outside_dir)


def test_get_file_content_security():
    # Setup: Ensure we have a file in UPLOAD_DIR
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    test_filename = "test_security_doc.pdf"
    test_file_path = os.path.join(UPLOAD_DIR, test_filename)
    with open(test_file_path, "w") as f:
        f.write("dummy content")

    try:
        # 1. Valid Access
        response = client.get(f"/api/file?path={test_file_path}")
        assert response.status_code == 200

        # 2. Path Traversal Attempt (../)
        # Construct path: UPLOAD_DIR/../uploads/test_security_doc.pdf (logically same)
        # valid traversal staying inside
        # But if we try to go out...

        # Let's try to access /etc/passwd or something relative to known location
        # This relies on where the runner is.
        # Let's create a file OUTSIDE the sandbox and try to reach it via traversal

        with tempfile.NamedTemporaryFile(delete=False) as secrets_file:
            secrets_file.write(b"SECRET")
            secrets_path = secrets_file.name

        try:
            # relative path from UPLOAD_DIR to secrets_file
            # This is hard to construct reliably across platforms without os.path.relpath
            rel_path = os.path.relpath(secrets_path, start=UPLOAD_DIR)

            # Attempt access using the relative path (which contains ../)
            # The API takes 'path', which can be absolute or relative.
            # If we pass absolute path to secret, it should fail.
            response = client.get(f"/api/file?path={secrets_path}")
            assert response.status_code == 403

            # If we pass relative path traversing out
            response = client.get(f"/api/file?path={os.path.join(UPLOAD_DIR, rel_path)}")
            assert response.status_code == 403

        finally:
            os.remove(secrets_path)

    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
