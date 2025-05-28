import pika
import os
import threading

from dotenv import load_dotenv
from summary import summarize_text
from api import get_diff, save_summary
from diff_parser import parse_diff_id

load_dotenv(override=True)
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_INPUT_QUEUE = os.getenv("RABBITMQ_INPUT_QUEUE")
RABBITMQ_OUTPUT_QUEUE = os.getenv("RABBITMQ_OUTPUT_QUEUE")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
PUBLISH_TO_OUTPUT_QUEUE = os.getenv("PUBLISH_TO_OUTPUT_QUEUE", "false").lower() == "true"

# RabbitMQ connection parameters
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection_params = pika.ConnectionParameters(
    host=RABBITMQ_HOST, credentials=credentials
)

def publish_llm_id(llm_id: int):
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # Ensure the output queue exists
    channel.queue_declare(queue=RABBITMQ_OUTPUT_QUEUE, durable=True)

    # Publish the summary to the output queue
    channel.basic_publish(
        exchange="",
        routing_key=RABBITMQ_OUTPUT_QUEUE,
        body=str(llm_id),
        properties=pika.BasicProperties(delivery_mode=2),  # make message persistent
    )
    connection.close()

def process_message(message, doc_diff_id, channel, delivery_tag):
    # Processing by the LLM (may take a few minutes)
    summary = summarize_text(message)
    print(f"Summary: {summary}", flush=True)

    # Publishing the summary to the api
    llm_id, is_successful = save_summary(doc_diff_id, summary)
    if not is_successful:
        print(f"Failed to save summary for diff ID {doc_diff_id}. Skipping.", flush=True)
        
    # Acknowledgment (ack) of message receipt
    #channel.basic_ack(delivery_tag=delivery_tag)

    # Publish llm_id to rabbit queue
    if PUBLISH_TO_OUTPUT_QUEUE:
        publish_llm_id(llm_id)


def on_data(ch, method, properties, body):
    # This function is called whenever a message is received.
    print(f"Received message: {body.decode()}", flush=True)

    diff_id = parse_diff_id(body)
    if diff_id is None:
        print("Invalid message: diff_id must be a numeric string. Skipping.", flush=True)
        #ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    
    diff = get_diff(diff_id)
    if diff is None:
        print(f"No diff found for ID {diff_id} or other internal problem. Skipping message.", flush=True)
        #ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    print(f"Fetched diff content for ID {diff_id}: {diff[:100]}...", flush=True)

    # Starting the function that processes the message in a separate thread
    worker = threading.Thread(
        target=process_message, args=(diff, diff_id, ch, method.delivery_tag)
    )
    worker.start()

    # Waiting for the thread to finish, but at the same time, processing events (heartbeats).
    while worker.is_alive():
        worker.join(timeout=1)
        ch.connection.process_data_events(time_limit=0.1)


def wait_for_data():
    # Establish connection for consuming
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # Declare a queue
    # The 'durable' parameter ensures that the queue will survive a broker restart.
    # If set to True, the queue will be recreated after a restart, preserving messages.
    channel.queue_declare(queue=RABBITMQ_INPUT_QUEUE, durable=True)

    # Set the prefetch count to limit the number of unacknowledged messages
    # This helps to control the flow of messages and ensures that the consumer
    # does not get overwhelmed. For example, if set to 1, the consumer will
    # only receive one message at a time until it acknowledges it.
    channel.basic_qos(prefetch_count=1)

    # Start consuming messages from the queue
    # The 'on_message_callback' parameter specifies the function to call when a message is received.
    # 'auto_ack=True' means that messages will be acknowledged automatically upon receipt.
    # If set to False, you will need to manually acknowledge messages after processing them.
    channel.basic_consume(
        queue=RABBITMQ_INPUT_QUEUE, on_message_callback=on_data, auto_ack=True
    )

    print("Waiting for messages. To exit press CTRL+C", flush=True)
    try:
        # Start the message consumption loop
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping consumption...")
    finally:
        connection.close()
