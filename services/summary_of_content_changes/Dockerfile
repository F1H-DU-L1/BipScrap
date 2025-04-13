FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

# Whether to stream model output live to stdout (true/false)
ENV SHOW_STREAM=true

# Host URL of the Ollama server
ENV OLLAMA_HOST=http://localhost:11434

# Maximum number of characters per text fragment sent to the model
ENV FRAGMENT_SIZE=3072

# Host URL of the RabbitMQ server
ENV RABBITMQ_HOST=localhost

# Name of the input queue for RabbitMQ where LLM input data is sent
ENV RABBITMQ_INPUT_QUEUE=llm_input_data

# Name of the output queue for RabbitMQ where LLM output data is received
ENV RABBITMQ_OUTPUT_QUEUE=llm_output_data


CMD ["python", "main.py"]
