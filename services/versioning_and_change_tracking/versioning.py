import pika
import json
import os
from dotenv import load_dotenv

# Wczytanie zmiennych środowiskowych
load_dotenv(override=True)

# Parametry połączenia z RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_INPUT_QUEUE = os.getenv("RABBITMQ_QUEUE", "data_queue")
RABBITMQ_OUTPUT_QUEUE = os.getenv("RABBITMQ_OUTPUT_QUEUE", "processed_queue")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "password")

# Połączenie z RabbitMQ
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Deklaracja kolejek (na wypadek, gdyby nie istniały)
channel.queue_declare(queue=RABBITMQ_INPUT_QUEUE, durable=True)
channel.queue_declare(queue=RABBITMQ_OUTPUT_QUEUE, durable=True)

print(f"🎧 Oczekiwanie na wiadomości w kolejce '{RABBITMQ_INPUT_QUEUE}'. Przesyłam do '{RABBITMQ_OUTPUT_QUEUE}'...\n")

# Funkcja skracająca tekst
def shorten_text(text, max_len=100):
    return text

# Callback – co robić z każdą wiadomością
def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        url = data.get('url', 'brak')
        text = data.get('text', '')
        short_text = shorten_text(text)

        print(f"\n🔗 URL: {url}")
        print(f"📉 Skrócony tekst: {short_text}")

        # Nowa wiadomość do wysłania
        processed_data = {
            "url": url,
            "short_text": short_text
        }

        # Publikacja do wyjściowej kolejki
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_OUTPUT_QUEUE,
            body=json.dumps(processed_data),
            properties=pika.BasicProperties(
                delivery_mode=2  # trwała wiadomość
            )
        )

        # Potwierdzenie odbioru wiadomości
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"❌ Błąd przetwarzania wiadomości: {e}")

# Ustawienie konsumenta
channel.basic_consume(queue=RABBITMQ_INPUT_QUEUE, on_message_callback=callback)

# Start nasłuchiwania
channel.start_consuming()
