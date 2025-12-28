import json
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


def upload_file_to_gemini(file_path: str, api_key: str = None, mime_type: str = None):
    """
    Uploads a file to the Gemini Files API.

    Args:
        file_path (str): The local path to the file to upload.
        api_key (str, optional): The Google API Key.
        mime_type (str, optional): The MIME type of the file. Defaults to None (auto-detect).

    Returns:
        The uploaded file object from the GenAI library.
    """
    print(f"Uploading file: {file_path}...")

    local_client = None
    if api_key:
        local_client = genai.Client(api_key=api_key)
    else:
        # Fallback to global client or env var
        global client
        if not client:
            key = os.getenv("GOOGLE_API_KEY")
            if key:
                client = genai.Client(api_key=key)
        local_client = client

    if not local_client:
        raise Exception("Google API Key not found. Cannot upload file.")

    # Using 'file' as the argument name for the local path
    uploaded_file = local_client.files.upload(file=file_path)
    print(f"File uploaded: {uploaded_file.display_name} as {uploaded_file.uri}")
    return uploaded_file


def wait_for_files_active(files, client=None):
    """
    Waits for the given files to be active on the Gemini API.

    Files uploaded to Gemini (especially larger PDFs) require processing time
    before they can be used in generation requests. This function polls the
    file status until it is 'ACTIVE'.

    Args:
        files (list): A list of uploaded file objects.
        client (genai.Client, optional): The client instance to use.

    Raises:
        Exception: If a file fails to process.
    """
    print("Waiting for file processing...")
    # Fallback to global if not provided
    if not client:
        client = globals().get("client")

    if not client:
        key = os.getenv("GOOGLE_API_KEY")
        if key:
            client = genai.Client(api_key=key)

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


def extract_data_with_gemini(file_path: str, user_prompt: str, metadata_schema: dict = None, api_key: str = None):
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
        metadata_schema (dict, optional): Schema for metadata extraction.
        api_key (str, optional): The Google API Key.

    Returns:
        str: The raw text response from the model (expected to be JSON).
    """
    local_client = None
    if api_key:
        local_client = genai.Client(api_key=api_key)
    else:
        # Fallback to global client or env var
        global client
        if not client:
            key = os.getenv("GOOGLE_API_KEY")
            if key:
                client = genai.Client(api_key=key)
        local_client = client

    if not local_client:
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
        myfile = upload_file_to_gemini(file_path, api_key=api_key)

        # 2. Wait for processing (needs client too, update wait function or use local_client directly?)
        # wait_for_files_active uses global client. We should update it too.
        # For now, let's update wait_for_files_active to take client or assume the global one is what it used before.
        # Actually, wait_for_files_active relies on 'client'. We should fix that too.
        # But wait, we can pass the client to wait_for_files_active.

        wait_for_files_active([myfile], client=local_client)

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
            " - 'metadata': (Optional) a dictionary containing extracted metadata fields if specific \n"
            "    schema provided. \n"
        )

        if metadata_schema:
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
        response = local_client.models.generate_content(model=MODEL_NAME, contents=[myfile, system_instruction])

        return response.text
    finally:
        # 4. Cleanup
        if myfile:
            try:
                print(f"Deleting file {myfile.name}...")
                local_client.files.delete(name=myfile.name)
                print(f"File {myfile.name} deleted.")
            except Exception as e:
                # Log the error but don't let cleanup failure crash the app
                print(f"Warning: Failed to delete file {myfile.name} from Gemini: {e}")
