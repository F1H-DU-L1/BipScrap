import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)
BASE_URL = os.getenv("DATA_MANAGEMENT_BASE_URL")


def get_diff(doc_diff_id: int) -> str | None:
    if not doc_diff_id:
        return None

    response = requests.get(f"{BASE_URL}/diff/{doc_diff_id}")

    if response.status_code == 200:
        return response.json().get("content")
    else:
        return None


def save_summary(doc_diff_id: int, summary: str) -> tuple[int | None, bool]:
    if not doc_diff_id:
        return None, False

    if not summary:
        return None, False

    payload = {"content": summary}

    response = requests.post(f"{BASE_URL}/summary/{doc_diff_id}", json=payload)

    if response.status_code == 200:
        llm_id = response.json().get('llm_id')
        return llm_id, True
    else:
        return None, False
