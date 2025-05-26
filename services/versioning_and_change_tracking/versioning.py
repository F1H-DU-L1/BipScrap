import json
import os
import time
import pika
import requests
import socket

from dotenv import load_dotenv

load_dotenv(override=True)
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBITMQ_INPUT_QUEUE = os.getenv("RABBITMQ_INPUT_QUEUE")
RABBITMQ_OUTPUT_QUEUE = os.getenv("RABBITMQ_OUTPUT_QUEUE")
DATA_MANAGEMENT_HOST = os.getenv("DATA_MANAGEMENT_HOST")
DATA_MANAGEMENT_PORT = os.getenv("DATA_MANAGEMENT_PORT")

def wait_for_service(host, port, timeout=60):
    print(f"Czekam na serwis {host}:{port} ...")
    start = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=5):
                print(f"Serwis {host}:{port} jest dostępny.")
                return
        except (socket.timeout, ConnectionRefusedError):
            if time.time() - start > timeout:
                raise TimeoutError(f"Timeout oczekiwania na {host}:{port}")
            print(f"Serwis {host}:{port} niedostępny, ponawiam próbę za 2s...")
            time.sleep(2)


credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue=RABBITMQ_INPUT_QUEUE, durable=True)
channel.queue_declare(queue=RABBITMQ_OUTPUT_QUEUE, durable=True)

def split_by_dot(text):
    return [part.strip() + '.' for part in text.split('.') if part.strip()]

def compare_documents(latest_doc, second_latest_doc):
    if not second_latest_doc:
        return latest_doc.strip()

    latest_sentences = split_by_dot(latest_doc)
    second_latest_set = set(split_by_dot(second_latest_doc))

    new_sentences = [s for s in latest_sentences if s not in second_latest_set]

    return ' '.join(new_sentences)

def fetch_documents(url):
    payload = {"url": url}
    response = requests.get(f"http://{DATA_MANAGEMENT_HOST}:{DATA_MANAGEMENT_PORT}/docs", json=payload)
    print(f"Kod odpowiedzi {response}")
    if response.status_code == 200:
        response_content = response.json()
        documents = response_content.get("documents", [])
        print(f"Otrzymane dokumenty {documents}")
        doc1, doc2 = documents
        if doc1 is None and doc2 is None:
            print("Brakuje dokumentów.")
        elif doc2 is None:
            diff_payload = {
                "doc_id_key_1": doc1["doc_id"],
                "doc_id_key_2": doc1["doc_id"],
                "content": doc1["content"]
            }
            diff_response = requests.post(f"http://{DATA_MANAGEMENT_HOST}:{DATA_MANAGEMENT_PORT}/diff",
                                          json=diff_payload)
            send_to_next_queue(doc1['doc_id'])
            print("Wysłano różnice:", diff_response.json())
        elif doc1 is not None and doc2 is not None:
            doc1 = documents[0]
            doc2 = documents[1]
            diff_result = compare_documents(doc1["content"], doc2["content"])
            if diff_result:
                diff_payload = {
                    "doc_id_key_1": doc1["doc_id"],
                    "doc_id_key_2": doc2["doc_id"],
                    "content": diff_result
                }
                diff_response = requests.post(f"http://{DATA_MANAGEMENT_HOST}:{DATA_MANAGEMENT_PORT}/diff",
                                              json=diff_payload)
                send_to_next_queue(doc1['doc_id'])
                print("Wysłano różnice:", diff_response.json())
            else:
                print(f"Brak różnic")
        else:
            print("Zbyt dużo dokumentów!")

        # if latest_doc and second_latest_doc:
        #     diff_result = compare_documents(latest_doc, second_latest_doc)
        #     if diff_result:
        #
        #         diff_payload = {
        #             "doc_id_key_1": doc_id_key_1,
        #             "doc_id_key_2": doc_id_key_2,
        #             "content": diff_result
        #         }
        #         diff_response = requests.post(f"http://{DATA_MANAGEMENT_HOST}:{DATA_MANAGEMENT_PORT}/diff", json=diff_payload)
        #         send_to_next_queue(doc_id_key_1)
        #         print("Wysłano różnice:", diff_response.json())
        #
        #     else:
        #         print("Brak nowych zdań.")
        # elif latest_doc:
        #     diff_payload = {
        #         "doc_id_key_1": doc_id_key_1,
        #         "doc_id_key_2": doc_id_key_2,
        #         "content": latest_doc
        #     }
        #     diff_response = requests.post(f"http://{DATA_MANAGEMENT_HOST}:{DATA_MANAGEMENT_PORT}/diff", json=diff_payload)
        #     send_to_next_queue(doc_id_key_1)
        #     print("Wysłano różnice:", diff_response.json())
        # else:
        #     print("Brakuje dokumentów.")
    else:
        print(f"Błąd pobierania dokumentów: {response.status_code}")
        print("Response:", response.text)

def callback(ch, method, properties, body):
        data = json.loads(body)
        url = data.get("url")

        print(f"Odebrano z kolejki: url={url}")
        fetch_documents(url)

def send_to_next_queue(doc_id_key):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        )
    )
    channel = connection.channel()
    next_queue = RABBITMQ_OUTPUT_QUEUE
    channel.queue_declare(queue=next_queue, durable=True)
    channel.basic_publish(exchange='', routing_key=next_queue, body=str(doc_id_key))
    connection.close()


def consume_queue():
    #wait_for_service(DATA_MANAGEMENT_HOST, DATA_MANAGEMENT_PORT)

    credentials = pika.PlainCredentials(username=RABBITMQ_USER, password=RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=5672,
        virtual_host='/',
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=RABBITMQ_INPUT_QUEUE, durable=True)

    channel.basic_consume(
        queue=RABBITMQ_INPUT_QUEUE,
        on_message_callback=callback,
        auto_ack=True
    )

    print("👂 Czekam na wiadomości...")
    channel.start_consuming()

if __name__ == "__main__":
    print("Uruchomiono")
    consume_queue()
