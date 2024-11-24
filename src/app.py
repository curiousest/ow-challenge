import os
import time
import requests
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from .processing_pytorch import calculate_credits_batch_pytorch
from .processing_pandas import calculate_credits_batch_pandas

app = FastAPI()

# Set default to PyTorch, but allow the choice to be overridden by an environment variable
CREDIT_CALCULATION_METHOD = os.getenv("CREDIT_CALCULATION_METHOD", "pytorch").lower()

MESSAGES_URL = os.getenv("MESSAGES_URL", "https://owpublic.blob.core.windows.net/tech-task/messages/current-period")
REPORTS_URL_TEMPLATE = os.getenv("REPORTS_URL_TEMPLATE", "https://owpublic.blob.core.windows.net/tech-task/reports/{report_id}")


class MessagesRequest(BaseModel):
    messages: List[str]


class UsageItem(BaseModel):
    message_id: int
    timestamp: str
    report_name: Optional[str] = None
    credits_used: float


class UsageResponse(BaseModel):
    usage: List[UsageItem]


def get_report_with_backoff(report_id: str, max_retries: int = 5, backoff_time: float = 0.5) -> Optional[dict]:
    """
    Retrieve a report with exponential backoff in case of request failures.

    Args:
        report_id (str): The ID of the report to retrieve.
        max_retries (int, optional): The maximum number of retry attempts. Defaults to 5.
        backoff_time (float, optional): The initial backoff time in seconds. Defaults to 0.5.

    Returns:
        Optional[dict]: The report data as a dictionary if successful, None if the report is not found or all retries fail.
    """
    for _ in range(max_retries):
        try:
            report_response = requests.get(REPORTS_URL_TEMPLATE.format(report_id=report_id))
            if report_response.status_code == 200:
                return report_response.json()
            if report_response.status_code == 404:
                return None
        except requests.exceptions.RequestException as e:
            # Log the exception or handle it as needed
            print(f"Request failed: {e}")
        time.sleep(backoff_time)
        backoff_time *= 2  # Exponential backoff
    return None


@app.get("/usage", response_model=UsageResponse)
def usage_endpoint():
    response = requests.get(MESSAGES_URL)
    if response.status_code != 200:
        return UsageResponse(usage=[])

    messages_data = response.json()["messages"]
    messages = []
    usage = []

    # First, gather messages and check for reports
    # Ideally, this would be done in parallel or one request, but we don't have enough context to make that decision now
    for message in messages_data:
        if "report_id" in message:
            report_data = get_report_with_backoff(message["report_id"])
            if report_data:
                usage.append(
                    UsageItem(
                        message_id=message["id"],
                        timestamp=message["timestamp"],
                        report_name=report_data.get("name"),
                        credits_used=report_data.get("credit_cost"),
                    )
                )
            else:
                messages.append(message)
        else:
            messages.append(message)

    # Process all messages that need credit calculation in a batch
    if messages:
        messages_text = [message["text"] for message in messages]
        if CREDIT_CALCULATION_METHOD == "pandas":
            credits = calculate_credits_batch_pandas(messages_text)
        else:
            credits = calculate_credits_batch_pytorch(messages_text)

        # Add calculated credits to usage
        for message, credit in zip(messages, credits):
            usage.append(
                UsageItem(
                    message_id=message["id"],
                    timestamp=message["timestamp"],
                    credits_used=credit,
                )
            )

    return UsageResponse(usage=usage)
