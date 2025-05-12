import requests
from datetime import datetime

url = "http://localhost:5000/uploadfulldoc"
payload = {
    "base_URL": "https://example.com",
    "scrap_datetime": datetime.now().isoformat(),
    "URL": "https://example.com/page1",
    "Content": "Some scraped content here."
}

response = requests.post(url, json=payload)
print(response.status_code)
print(response.json())