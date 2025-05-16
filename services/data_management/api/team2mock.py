import requests
from datetime import datetime

url = "http://localhost:5000/docs"
payload = {
    "url": "https://example.com/page1"
}

response = requests.get(url, json=payload)
print(response.status_code)
print(response.json())