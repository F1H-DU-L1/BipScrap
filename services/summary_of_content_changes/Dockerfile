FROM python:3.11-slim

WORKDIR /app

COPY services/summary_of_content_changes/requirements.txt .

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY services/summary_of_content_changes .

# Skopiowanie skryptu wait-for-it.sh
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

COPY services/summary_of_content_changes/wait-for-ollama.sh /usr/local/bin/wait-for-ollama.sh
RUN chmod +x /usr/local/bin/wait-for-ollama.sh

# Whether to stream model output live to stdout (true/false)
ENV SHOW_STREAM=true

# Host URL of the Ollama server
ENV OLLAMA_HOST=http://ollama:11434

# Maximum number of characters per text fragment sent to the model
ENV FRAGMENT_SIZE=3072

CMD ["sh", "-c", "wait-for-it.sh rabbitmq:5672 --timeout=30 --strict -- && wait-for-it.sh ollama:11434 --timeout=7000 --strict -- python main.py"]
