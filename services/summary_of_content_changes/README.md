# Text Summarization via RabbitMQ and Ollama
This project processes provided documents into summaries using an LLM.

## How It Works
1. The app listens for messages on the input RabbitMQ queue (`RABBITMQ_INPUT_QUEUE`).
2. Upon receiving a message (diff_id), it fetches the corresponding diff content from the database via the `DATA_MANAGEMENT_BASE_URL` API.
3. The retrieved content is split into fragments of size defined by `FRAGMENT_SIZE`.
4. Each fragment is summarized individually using the LLM via the Ollama interface.
5. The partial summaries are then merged into a single cohesive summary.
6. The final summary is saved to the database using the API.
7. If `PUBLISH_TO_OUTPUT_QUEUE` is set to true, the returned llm_id is published to the output RabbitMQ queue (`RABBITMQ_OUTPUT_QUEUE`).

## .env
```
# RabbitMQ server address
RABBITMQ_HOST=""

# Input queue
RABBITMQ_INPUT_QUEUE="t3in"

# Output queue 
RABBITMQ_OUTPUT_QUEUE="t3out"

# RabbitMQ user
RABBITMQ_USER="guest"

# RabbitMQ password
RABBITMQ_PASS="guest"

# Ollama server address
OLLAMA_HOST=ollama

# Ollama model, available models listed in the `Supported Models` section
OLLAMA_MODEL="llama3.1:8b"

# API address of the database
DATA_MANAGEMENT_BASE_URL="http://data_management:5000"

# Sends llm_id to the output queue; enable if there is a downstream microservice
PUBLISH_TO_OUTPUT_QUEUE=false
```

## Supported Models
The default and recomended model is:
- `llama3.1:8b`

Other models that can work well:
- `llama3.2`
- `hf.co/mradermacher/PLLuM-12B-nc-instruct-GGUF`
- `hf.co/mradermacher/PLLuM-8x7B-nc-instruct-GGUF`

