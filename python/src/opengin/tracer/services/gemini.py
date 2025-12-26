import os
import time

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    # Fallback/Warning if key is not present, though usually expected in env
    print("Warning: GOOGLE_API_KEY not found in environment variables.")

genai.configure(api_key=GOOGLE_API_KEY)

# Use a model that supports file input and JSON generation if possible,
# or just standard robust text generation. 1.5-flash is good for speed/cost.
MODEL_NAME = "gemini-2.0-flash"


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
    uploaded_file = genai.upload_file(file_path, mime_type=mime_type)
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
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()


def extract_data_with_gemini(file_path: str, user_prompt: str):
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
    if not GOOGLE_API_KEY:
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

    # 1. Upload File
    # Determine mime type or let library guess. For simplicity, we let it guess or strictly handle common types.
    myfile = upload_file_to_gemini(file_path)

    # 2. Wait for processing
    wait_for_files_active([myfile])

    # 3. Generate Content
    model = genai.GenerativeModel(model_name=MODEL_NAME)

    # System/Structural Prompt to guide the output format
    # We want to encourage structured output: Metadata (JSON), Tables (CSV), Stats.
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
        "Do not include markdown code blocks (like ```json) in the response if possible, "
        "or ensure it is valid JSON inside. "
        f"\n\nUser Request: {user_prompt}"
    )

    response = model.generate_content([myfile, system_instruction])

    # 4. Cleanup (Best practice: delete file after use to save storage limit context)
    # However, for this MVP we might leave it or delete it. Let's delete to be clean.
    # genai.delete_file(myfile.name) # Uncomment if strict cleanup is desired immediately

    return response.text
