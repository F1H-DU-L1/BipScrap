# API to save data in DB

## How  to install
Using venv:
- ```cd data_management``` (adjust path)
- ```py -3 -m venv .venv```
- ```.venv\Scripts\activate``` (depending on OS)
- ```pip install -r requirements.txt```

## How to run
- ```cd api```
- ```flask --app api run```

## Developing
- ```flask --app api run --debug```
## .env
DATABASE_URL=postgresql://user:password@db:5432/baza

## Endpoints

### Team 1

- Upload scrap data to DB
  #### POST `/fulldoc`
    - Request body:
        ```json
        {
            "base_url": "https://example.com",
            "scrap_datetime": "",
            "url": "https://example.com",
            "content": "Example content",
        }
        ```
    - Response:
        ```json
        {
            "message": "Document saved successfully"
        }
        ```

### Team 2
- Get 2 lastest docs
    #### GET `/docs`
    - Request body:
        ```json
        {
            "url": "https://example.com"
        }
        ```
    - Response:
        ```json
        {
            "documents": [
                {
                    "doc_id_key": 1,
                    "content": "Example content",
                },
                {
                    "doc_id_key": 11,
                    "content": "Example content, newer content",
                }
            ]
        }
        ```
- Diff saving
    #### POST `/diff`
    - Request body:
        ```json
        {
            "doc_id_key_1": 1,
            "doc_id_key_2": 11,
            "content": "Example diff",
        }
        ```
    - Response:
        ```json
        {
            "message": "Diff saved successfully",
            "doc_diff_id": 1
        }
        ```

### Team 3
- Get diff
    #### GET `/diff/<doc_diff_id>`
    - Request body:
        No body
    - Response:
        ```json
        {
            "content": "Example diff"
        }
        ```

- Save LLM summary
    #### POST `/summary/<doc_diff_id>`
    - Request body:
        ```json
        {
            "content": "Example summary",
        }
        ```
    - Response:
        ```json
        {
            "message": "Summary saved successfully",
            "llm_id": 1
        }
        ```
