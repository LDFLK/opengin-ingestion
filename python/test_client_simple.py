import requests

url = "http://localhost:8000/graphql"

query = """
    query {
        hello
    }
"""

print("Sending Hello Query...")
try:
    response = requests.post(url, json={"query": query})
    print("Status:", response.status_code)
    print("Body:", response.text)
except Exception as e:
    print("Error:", e)
