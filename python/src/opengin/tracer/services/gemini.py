import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = None
if not GOOGLE_API_KEY:
    # Fallback/Warning if key is not present, though usually expected in env
    print("Warning: GOOGLE_API_KEY not found in environment variables.")
else:
    client = genai.Client(api_key=GOOGLE_API_KEY)

# Use a model that supports file input and JSON generation if possible,
# or just standard robust text generation. 1.5-flash is good for speed/cost.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def upload_file_to_gemini(file_path: str, mime_type: str = None):
    """
    Uploads a file to the Gemini Files API.

    Args:
        file_path (str): The local path to the file to upload.
        mime_type (str, optional): The MIME type of the file. Defaults to None (auto-detect).

    Returns:
        The uploaded file object from the GenAI library.
    """
    print(f"Uploading file: {file_path}...")
    # New SDK: client.files.upload(file=...)
    # Note: 'path' argument might be used or 'file'. based on docs usually 'file' or 'path'.
    # Let's try 'file' as generic, or check quickly?
    # Actually, standard python client uses 'file' for path often or 'path'.
    # Safe bet: use positional if unsure, or try 'path'.
    # Recent google-genai documentation suggests 'file' or 'path'.

    # Using 'file' as the argument name for the local path
    uploaded_file = client.files.upload(file=file_path)
    print(f"File uploaded: {uploaded_file.display_name} as {uploaded_file.uri}")
    return uploaded_file


def wait_for_files_active(files):
    """
    Waits for the given files to be active on the Gemini API.

    Files uploaded to Gemini (especially larger PDFs) require processing time
    before they can be used in generation requests. This function polls the
    file status until it is 'ACTIVE'.

    Args:
        files (list): A list of uploaded file objects.

    Raises:
        Exception: If a file fails to process.
    """
    print("Waiting for file processing...")
    for f in files:
        # In new SDK, file object might have .name
        name = f.name
        remote_file = client.files.get(name=name)

        while remote_file.state == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            remote_file = client.files.get(name=name)

        if remote_file.state != "ACTIVE":
            raise Exception(f"File {remote_file.name} failed to process: {remote_file.state}")
    print("...all files ready")
    print()


def extract_data_with_gemini(file_path: str, user_prompt: str, metadata_schema: dict = None):
    """
    Uploads a file to Gemini and performs data extraction.

    This function handles the full interaction lifecycle with the Gemini API:
    1. Checks for API key (exits to Mock Mode if missing).
    2. Uploads the file.
    3. Waits for processing.
    4. Constructs a system prompt enforcing strictly valid JSON output.
    5. Sends the generation request with the user's extraction prompt.

    Args:
        file_path (str): Path to the single-page PDF or image.
        user_prompt (str): Specific instructions on what to extract.

    Returns:
        str: The raw text response from the model (expected to be JSON).
    """
    # If no API key is set, return a mock response for testing purposes
    if not client:
        print("Mocking Gemini response (No API Key found)")
        return """
        {
          "tables": [
            {
              "id": "table_1",
              "name": "Invoice Items",
              "columns": ["Item", "Quantity", "Price"],
              "rows": [
                ["Widget A", "2", "$10.00"],
                ["Widget B", "1", "$25.00"]
              ]
            }
          ]
        }
        """

    myfile = None
    try:
        # 1. Upload File
        myfile = upload_file_to_gemini(file_path)

        # 2. Wait for processing
        wait_for_files_active([myfile])

        # 3. Generate Content
        # System/Structural Prompt to guide the output format
        system_instruction = (
            "You are a document extraction assistant. "
            "Analyze the uploaded document and extract all tables found. "
            "Please provide your response in a strictly valid JSON format. "
            "The JSON should contain a key 'tables' which is a list of table objects. "
            "Each table object must have: \n"
            " - 'id': a unique string identifier for the table\n"
            " - 'name': a descriptive name for the table (inferred from context or title)\n"
            " - 'columns': a list of strings representing the column headers\n"
            " - 'rows': a list of lists of strings, representing the data rows matching the columns order. \n"
            " - 'metadata': (Optional) a dictionary containing extracted metadata fields if specific schema provided. \n"
        )

        if metadata_schema:
            import json
            schema_str = json.dumps(metadata_schema, indent=2)
            system_instruction += (
                f"\n\nPer Table Metadata Extraction:\n"
                f"For each table identified, you must also extract metadata based on the following schema:\n"
                f"{schema_str}\n"
                "The extracted metadata should be placed in the 'metadata' key within each table object.\n"
            )

        system_instruction += (
            "Do not include markdown code blocks (like ```json) in the response if possible, "
            "or ensure it is valid JSON inside. "
            f"\n\nUser Request: {user_prompt}"
        )

        # New SDK generation
        # client.models.generate_content(model=..., contents=[...])
        response = client.models.generate_content(model=MODEL_NAME, contents=[myfile, system_instruction])

        return response.text
    finally:
        # 4. Cleanup
        if myfile:
            try:
                print(f"Deleting file {myfile.name}...")
                client.files.delete(name=myfile.name)
                print(f"File {myfile.name} deleted.")
            except Exception as e:
                # Log the error but don't let cleanup failure crash the app
                print(f"Warning: Failed to delete file {myfile.name} from Gemini: {e}")
