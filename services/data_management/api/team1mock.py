import requests
from datetime import datetime

url = "http://localhost:5000/fulldoc"
payload = {
    "base_url": "https://example.com",
    "scrap_datetime": datetime.now().isoformat(),
    "url": "https://example.com/page1",
    "content": "Some scraped content here."
}

response = requests.post(url, json=payload)
print(response.status_code)
print(response.json())