import ollama
from enum import Enum
import re
import os

# Constants (read from environment variables)
SHOW_STREAM = os.getenv("SHOW_STREAM", "false").lower() == "true"
OLLAMA_HOST = os.getenv("OLLAMA_HOST")
FRAGMENT_SIZE = int(os.getenv("FRAGMENT_SIZE", "3072"))

# Create enumeration for models
Model = Enum(
    "Models",
    [
        ("llama3_2_3b", "llama3.2"),
        ("llama3_1_8b", "llama3.1:8b"),
        ("pllum_12b", "hf.co/mradermacher/PLLuM-12B-nc-instruct-GGUF"),
        ("pllum_8x7b", "hf.co/mradermacher/PLLuM-8x7B-nc-instruct-GGUF"),
    ],
)

# Initialize the client using the constant host URL
client = ollama.Client(host=OLLAMA_HOST)


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


def create_summary(content: str, model: Model) -> str:
    """
    Create a summary of the given content.

    Args:
        content (str): The content to summarize.
        model (Model): The model to be used for generating the summary.

    Returns:
        str: The summary of the content.
    """
    # Create the chat stream; the system message instructs the assistant to read long documents
    # and generate a summary in one paragraph.
    stream = client.chat(
        model=model.value,
        messages=[
            {
                "role": "system",
                "content": "Jesteś asystentem, który potrafi czytać długie dokumenty i przygotowywać streszczenia akapitach",
            },
            {"role": "user", "content": content},
        ],
        stream=True,
        # options={"num_predict": 1024*128}
    )

    # Collect and return the aggregated summary using the helper function
    return aggregate_stream_response(stream)


def create_final_summary(summaries: list[str], model: Model) -> str:
    """
    Create a final summary by combining individual summaries.

    Args:
        summaries (list[str]): The list of individual summaries.
        model (Model): The model to be used for generating the final summary.

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
        model=model.value,
        messages=[
            {
                "role": "system",
                "content": "Jesteś asystentem, który potrafi czytać długie dokumenty, które są podzielone na "
                "mniejsze fragmenty i przygotowywać podsumowanie, które to jest napisany spójnie.",
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


def summarize_text(content: str, model: Model = Model.llama3_1_8b) -> str:
    """
    Summarizes a long input text by splitting it into fragments, summarizing each fragment,
    and combining the summaries into a final summary.

    Args:
        content (str): The full input text to summarize.
        model (Model): The model used for summarization.

    Returns:
        str: The final summarized result.
    """

    # Split the content into fragments of at most FRAGMENT_SIZE characters
    fragments = text_fragments(content, FRAGMENT_SIZE)

    # Generate summary for each fragment
    fragment_summaries = []
    for i, fragment in enumerate(fragments):
        print(f"\n[INFO] Summarizing fragment {i + 1}/{len(fragments)}...")
        summary = create_summary(fragment, model)
        fragment_summaries.append(summary)

    # Merge all fragment summaries into a final summary
    if(len(fragment_summaries) == 1):
        print("\n[INFO] Only one fragment summary available. No need to merge.")
        return fragment_summaries[0]
    
    final_summary = create_final_summary(fragment_summaries, model)
    return final_summary

