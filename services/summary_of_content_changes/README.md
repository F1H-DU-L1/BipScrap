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
RABBITMQ_HOST=rabbitmq

# Input queue
RABBITMQ_INPUT_QUEUE=t2t3

# Output queue
RABBITMQ_OUTPUT_QUEUE=t3out

# RabbitMQ user
RABBITMQ_USER=admin

# RabbitMQ password
RABBITMQ_PASS=admin

# Ollama server address
OLLAMA_HOST=ollama

# Ollama model, available models listed in the `Supported Models` section
OLLAMA_MODEL="llama3.1:8b"

# Character limit after which the content is split into fragments. It’s best to set this to 50% of the model's context size. The default value of 3072 should yield correct results.
FRAGMENT_SIZE="3072"

# Whether to display the LLM output in real-time as it is being generated.
SHOW_STREAM="false"

# Prompt used for summarizing a single document fragment
FRAGMENT_SUMMARY_PROMPT="Jesteś asystentem, który potrafi czytać długie dokumenty i przygotowywać streszczenia w akapitach."

# Prompt used for merging multiple fragment summaries into a cohesive summary
FINAL_SUMMARY_PROMPT= "Jesteś asystentem, który potrafi czytać długie dokumenty, podzielone na mniejsze fragmenty i przygotowywać podsumowanie, które jest napisane spójnie."

# API address of the database
DATA_MANAGEMENT_BASE_URL="http://data_management:5000"

# Sends llm_id to the output queue; enable if there is a downstream microservice
PUBLISH_TO_OUTPUT_QUEUE="true"
```

## Supported Models
The default and recomended model is:
- `llama3.1:8b`

Other models that can work well:
- `llama3.2`
- `hf.co/mradermacher/PLLuM-12B-nc-instruct-GGUF`
- `hf.co/mradermacher/PLLuM-8x7B-nc-instruct-GGUF`

