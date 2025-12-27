from unittest.mock import MagicMock, patch

import pytest

from opengin.tracer.services.gemini import extract_data_with_gemini

# Since gemini.py initializes 'client' at module level based on env var,
# we need to be careful. If GOOGLE_API_KEY is missing, client is None.
# We'll use patch to force the client to exist during the test.


@pytest.fixture
def mock_gemini_client():
    with patch("opengin.tracer.services.gemini.client") as mock_client:
        # User reported warning if key missing, but we want to simulate key present logic
        # If client is None in the module, patch might just mock 'None'.
        # Better to patch where it is used or force it.
        # However, extract_data_with_gemini checks "if not client:"

        # Ensure the mock behaves like a genai.Client
        mock_client.files.upload.return_value = MagicMock(name="uploaded_file", uri="http://uri")
        mock_client.files.upload.return_value.name = "files/123"

        mock_client.models.generate_content.return_value.text = "{}"

        yield mock_client


def test_extract_data_cleanup_success(mock_gemini_client):
    """
    Test that file is deleted after successful generation.
    """
    # Mock helper functions to avoid their logic/prints
    with (
        patch("opengin.tracer.services.gemini.upload_file_to_gemini") as mock_upload,
        patch("opengin.tracer.services.gemini.wait_for_files_active"),
    ):

        # Setup mock file returned by upload
        mock_file = MagicMock()
        mock_file.name = "files/test_file"
        mock_upload.return_value = mock_file

        # Call function
        extract_data_with_gemini("dummy_path.pdf", "prompt")

        # Assertions
        mock_upload.assert_called_once()
        mock_gemini_client.models.generate_content.assert_called_once()

        # Verify cleanup
        mock_gemini_client.files.delete.assert_called_once_with(name="files/test_file")


def test_extract_data_cleanup_on_failure(mock_gemini_client):
    """
    Test that file is deleted even if generation raises an exception.
    """
    with (
        patch("opengin.tracer.services.gemini.upload_file_to_gemini") as mock_upload,
        patch("opengin.tracer.services.gemini.wait_for_files_active"),
    ):

        mock_file = MagicMock()
        mock_file.name = "files/fail_file"
        mock_upload.return_value = mock_file

        # Make generation fail
        mock_gemini_client.models.generate_content.side_effect = Exception("Generation failed")

        # Call function and expect exception
        with pytest.raises(Exception, match="Generation failed"):
            extract_data_with_gemini("dummy_path.pdf", "prompt")

        # Verify cleanup still happened
        mock_gemini_client.files.delete.assert_called_once_with(name="files/fail_file")
