import pika
import json
import os
import hashlib
import difflib
from dotenv import load_dotenv

# Wczytanie zmiennych środowiskowych
load_dotenv(override=True)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_INPUT_QUEUE = os.getenv("RABBITMQ_QUEUE", "data_queue")
RABBITMQ_OUTPUT_QUEUE = os.getenv("RABBITMQ_OUTPUT_QUEUE", "processed_queue")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "password")

CACHE_DIR = "short_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Pomocnicze funkcje
def shorten_text(text, max_len=100):
    return text  # na razie nie skracamy, ale można dodać

def url_to_filename(url):
    return os.path.join(CACHE_DIR, hashlib.sha256(url.encode()).hexdigest() + ".json")

def get_previous_short_text(url):
    path = url_to_filename(url)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("short_text")
    return None

def save_current_short_text(url, short_text):
    path = url_to_filename(url)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"url": url, "short_text": short_text}, f, indent=2)

def print_diff(old, new):
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    diff = difflib.unified_diff(old_lines, new_lines, lineterm='', fromfile='previous', tofile='current')
    print("\n".join(diff))

def load_sample_data(file_path="sample.json"):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Połączenie z RabbitMQ
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue=RABBITMQ_INPUT_QUEUE, durable=True)
channel.queue_declare(queue=RABBITMQ_OUTPUT_QUEUE, durable=True)

print(f"🎧 Oczekiwanie na wiadomości w kolejce '{RABBITMQ_INPUT_QUEUE}'. Przesyłam do '{RABBITMQ_OUTPUT_QUEUE}'...\n")

def callback(ch, method, properties, body):
    try:
        # Ładujemy dane z kolejki
        data = json.loads(body)
        url = data.get('url', 'brak')
        text = data.get('text', '')
        short_text = shorten_text(text)

        print(f"\n🔗 URL: {url}")
        print(f"📉 Skrócony tekst: {short_text[:100]}{'...' if len(short_text) > 100 else ''}")

        # Załaduj dane z sample.json
        sample_data = load_sample_data()
        sample_entry = next((item for item in sample_data if item['url'] == url), None)

        previous = sample_entry['short_text'] if sample_entry else None

        if previous is None:
            print("🆕 Nie znaleziono pasującego URL w sample.json – nowy wpis.")
            diff_result = short_text
        elif previous != short_text:
            print("⚠️ Zmiana treści wykryta:")
            old_lines = previous.splitlines()
            new_lines = short_text.splitlines()
            diff_lines = list(
                difflib.unified_diff(old_lines, new_lines, lineterm='', fromfile='previous', tofile='current'))

            # Filtrujemy tylko nowe linie (zaczynające się od +), ale pomijamy metadane diff'a (np. +++ current)
            added_lines = [
                line[1:] for line in diff_lines
                if line.startswith("+") and not line.startswith("+++")
            ]

            if added_lines:
                diff_result = "\n".join(added_lines)
                print(diff_result)
            else:
                print("🚫 Brak znaczącej różnicy.")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
        else:
            print("✅ Brak zmian w `short_text`.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Publikacja tylko różnicy do wyjściowej kolejki
        processed_data = {
            "url": url,
            "diff": diff_result
        }
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_OUTPUT_QUEUE,
            body=json.dumps(processed_data),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        # Potwierdzenie odbioru wiadomości
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"❌ Błąd przetwarzania wiadomości: {e}")


channel.basic_consume(queue=RABBITMQ_INPUT_QUEUE, on_message_callback=callback)
channel.start_consuming()
