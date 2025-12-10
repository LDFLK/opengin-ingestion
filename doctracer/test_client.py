import requests
import json

url = "http://localhost:8000/graphql"

query = """
    mutation UploadAndExtract($file: Upload!, $prompt: String!) {
      extractData(file: $file, prompt: $prompt) {
        message
        rawResponse
        tables {
          id
          name
          columns
          rows
        }
      }
    }
"""

variables = {
    "file": None, 
    "prompt": "Extract all tables from this document."
}

# The operations payload (GraphQL query + variables)
operations_payload = {
    "query": query,
    "variables": variables
}

# The file mapping for multipart request (map variable 'file' in variables to part '0')
# Ideally standard GraphQL multipart spec uses 'operations', 'map', and file parts.
# Let's try the standard spec first.
# 1. operations: JSON string
# 2. map: JSON string mapping file keys (like "0") to variable paths (like ["variables.file"])
# 3. file part: the file content

multipart_data = {
    "operations": (None, json.dumps(operations_payload), "application/json"),
    "map": (None, json.dumps({"0": ["variables.file"]}), "application/json"),
    "0": ("data/simple.pdf", open("data/simple.pdf", "rb"), "application/pdf")
}

print("Sending request to GraphQL API...")
try:
    response = requests.post(url, files=multipart_data)
    print("Status Code:", response.status_code)
    
    try:
        data = response.json()
        print("Response JSON:")
        print(json.dumps(data, indent=2))
        
        if "errors" in data:
            print("Errors found in response!")
        else:
            extracted = data.get("data", {}).get("extractData", {})
            print("\n--- Extracted Tables ---")
            for table in extracted.get("tables", []):
                print(f"Table ID: {table['id']}")
                print(f"Name: {table['name']}")
                print(f"Columns: {table['columns']}")
                print(f"Rows: {len(table['rows'])} found")
                # print(table['rows']) 
                print("-" * 20)
                
    except json.JSONDecodeError:
        print("Failed to parse JSON response:")
        print(response.text)
        
except Exception as e:
    print("Error:", e)
