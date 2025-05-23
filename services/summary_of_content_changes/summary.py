import ollama
from enum import Enum
import re
import os
import sys
from dotenv import load_dotenv

# Constants (read from environment variables)
load_dotenv(override=True)
SHOW_STREAM = os.getenv("SHOW_STREAM", "false").lower() == "true"
OLLAMA_HOST = os.getenv("OLLAMA_HOST")
FRAGMENT_SIZE = int(os.getenv("FRAGMENT_SIZE", "3072"))
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
FRAGMENT_SUMMARY_PROMPT = os.getenv("FRAGMENT_SUMMARY_PROMPT", "create summary")
FINAL_SUMMARY_PROMPT = os.getenv("FINAL_SUMMARY_PROMPT", "create summary")

# Initialize the client using the constant host URL
client = ollama.Client(host=OLLAMA_HOST)


# Internal cache to store the verified model name
_verified_model = None

def get_model() -> str:
    """
    Return the verified model name.
    Only on the first call, check if the model exists or needs to be pulled.
    """
    global _verified_model

    if _verified_model is not None:
        return _verified_model

    model_name = OLLAMA_MODEL

    # List existing models and extract their names
    models = client.list()["models"]
    available_model_names = [model.model for model in models]

    print(f"Available models: {available_model_names}", flush=True)

    if model_name not in available_model_names:
        print(f"Model '{model_name}' not found locally. Attempting to pull...", flush=True)
        try:
            client.pull(model_name)
            print(f"Model '{model_name}' successfully pulled.", flush=True)
        except Exception as e:
            print(f"Error pulling model '{model_name}': {e}", flush=True)
            print("Model does not exist or cannot be pulled. Exiting.", flush=True)
            sys.exit(1)
    else:
        print(f"Model '{model_name}' is already available.", flush=True)

    _verified_model = model_name
    return _verified_model


def aggregate_stream_response(stream) -> str:
    """
    Aggregate message content from a given chat stream.

    Args:
        stream (Iterable[dict]): Stream of message chunks from the client.

    Returns:
        str: The aggregated response message.
    """
    aggregated_response = ""
    if SHOW_STREAM:
        print("\n")

    for chunk in stream:
        if SHOW_STREAM:
            print(chunk["message"]["content"], end="", flush=True)
        aggregated_response += chunk["message"]["content"]
    return aggregated_response


def create_summary(content: str) -> str:
    """
    Create a summary of the given content.

    Args:
        content (str): The content to summarize.

    Returns:
        str: The summary of the content.
    """
    # Create the chat stream; the system message instructs the assistant to read long documents
    # and generate a summary in one paragraph.
    stream = client.chat(
        model=get_model(),
        messages=[
            {
                "role": "system",
                "content": FRAGMENT_SUMMARY_PROMPT,
            },
            {"role": "user", "content": content},
        ],
        stream=True,
        # options={"num_predict": 1024*128}
    )

    # Collect and return the aggregated summary using the helper function
    return aggregate_stream_response(stream)


def create_final_summary(summaries: list[str]) -> str:
    """
    Create a final summary by combining individual summaries.

    Args:
        summaries (list[str]): The list of individual summaries.

    Returns:
        str: The final combined summary.
    """

    # Check if the combined summaries exceed the model's token limit
    # and concatenate them as a single message if necessary.
    combined_summaries = "\n".join(summaries)
    if len(combined_summaries) > FRAGMENT_SIZE:
        print(
            "[WARNING] Combined summaries exceed the model's token limit. Merging them into a single message."
        )
        return combined_summaries

    # Create the chat stream; the system message instructs the assistant to merge smaller fragments
    # of text into a coherent final summary.
    stream = client.chat(
        model=get_model(),
        messages=[
            {
                "role": "system",
                "content": FINAL_SUMMARY_PROMPT,
            },
            {"role": "user", "content": "\n".join(summaries)},
        ],
        stream=True,
        # options={"num_predict": 1024*128}
    )

    # Collect and return the aggregated final summary using the helper function
    return aggregate_stream_response(stream)


def text_fragments(content: str, divider: int) -> list[str]:
    """
    Divide the content into fragments of a specified character length without splitting words (splits only at whitespace boundaries).

    Args:
        content (str): The content to divide.
        divider (int): The maximum number of characters per fragment.

    Returns:
        list[str]: A list of content fragments.
    """
    fragments = []
    current_fragment = ""

    for word in re.split(r"(\s+)", content):
        if len(current_fragment) + len(word) <= divider:
            current_fragment += word
        else:
            if current_fragment.strip():
                fragments.append(current_fragment.strip())
            current_fragment = word

    if current_fragment.strip():
        fragments.append(current_fragment.strip())

    return fragments


def summarize_text(content: str) -> str:
    """
    Summarizes a long input text by splitting it into fragments, summarizing each fragment,
    and combining the summaries into a final summary.

    Args:
        content (str): The full input text to summarize.

    Returns:
        str: The final summarized result.
    """

    # Split the content into fragments of at most FRAGMENT_SIZE characters
    fragments = text_fragments(content, FRAGMENT_SIZE)

    # Generate summary for each fragment
    fragment_summaries = []
    for i, fragment in enumerate(fragments):
        print(f"\n[INFO] Summarizing fragment {i + 1}/{len(fragments)}...")
        summary = create_summary(fragment)
        fragment_summaries.append(summary)

    # Merge all fragment summaries into a final summary
    if len(fragment_summaries) == 1:
        print("\n[INFO] Only one fragment summary available. No need to merge.")
        return fragment_summaries[0]

    final_summary = create_final_summary(fragment_summaries)
    return final_summary
