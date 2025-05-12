import requests
from datetime import datetime

url = "http://localhost:5000/getdocs"
payload = {
    "URL": "https://example.com/page1"
}

response = requests.post(url, json=payload)
print(response.status_code)
print(response.json())