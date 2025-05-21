# Text Summarization via RabbitMQ and Ollama

This project enables asynchronous summarization of long texts using LLM models (e.g., LLaMA 3, PLLuM) and RabbitMQ message queues for communication.

## .env

```
RABBITMQ_HOST= ""
RABBITMQ_INPUT_QUEUE= "t1t2"
RABBITMQ_OUTPUT_QUEUE= ""
RABBITMQ_USER= ""
RABBITMQ_PASS= ""
OLLAMA_HOST=ollama
OLLAMA_MODEL="llama3.1:8b / llama3.2:latest / hf.co/mradermacher/PLLuM-8x7B-nc-instruct-GGUF:latest / hf.co/mradermacher/PLLuM-12B-nc-instruct-GGUF:latest"
DATA_MANAGEMENT_BASE_URL="http://data_management:5000"
```

## Installation

1. Clone the repository:

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the following content:
   ```ini
   RABBITMQ_USER=guest
   RABBITMQ_PASS=guest
   ```

## Running the Application

To start listening for messages and summarizing text:

```bash
python main.py
```

The script will start listening to the input RabbitMQ queue and will automatically process any received text.

## Sending Data to the Queue

You can use any RabbitMQ client (e.g., Python’s `pika`) to send a message with the text you want to summarize.

Example (Python):

```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='input_queue', durable=True)

text_to_summarize = "Your long text goes here..."
channel.basic_publish(
    exchange='',
    routing_key='input_queue',
    body=text_to_summarize.encode(),
    properties=pika.BasicProperties(delivery_mode=2)
)

connection.close()
```

## Retrieving the Summary

The generated summary will be published to the output queue (`output_queue`). You can receive it using a consumer like this:

```python
def callback(ch, method, properties, body):
    print("Received summary:\n", body.decode())

channel.basic_consume(queue='output_queue', on_message_callback=callback, auto_ack=True)
channel.start_consuming()
```

## How It Works

1. The app listens for messages on the input RabbitMQ queue (`input_queue`).
2. When it receives a message, it splits the content into fragments (`FRAGMENT_SIZE`).
3. Each fragment is summarized individually using the LLM via the Ollama interface.
4. Partial summaries are merged into a final cohesive summary.
5. The result is published to the output queue (`output_queue`).

## Supported Models

The default model is:
- `llama3.1:8b`

Other models listed in `summary.py` include:
- `llama3.2`
- `hf.co/mradermacher/PLLuM-12B-nc-instruct-GGUF`
- `hf.co/mradermacher/PLLuM-8x7B-nc-instruct-GGUF`

## Example Log Output

```bash
Waiting for messages. To exit press CTRL+C
Received message: Lorem ipsum dolor sit amet...
[INFO] Summarizing fragment 1/3...
[INFO] Summarizing fragment 2/3...
[INFO] Summarizing fragment 3/3...
Summary: Lorem ipsum summary...
```
