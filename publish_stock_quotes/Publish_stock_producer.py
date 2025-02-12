import os
import time
import json
import requests
from google.cloud import pubsub_v1
from datetime import datetime
import pytz
import finnhub


FINNHUB_API_KEY = "ct9kfs1r01quh43o9jl0ct9kfs1r01quh43o9jlg"
PUBSUB_TOPIC = "stock_data_topic"
GCP_PROJECT = "stock-data-project-449518"
STOCK_SYMBOL = "AAPL"
PUBLISH_INTERVAL_SEC = 60
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(GCP_PROJECT, PUBSUB_TOPIC)


publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(GCP_PROJECT, PUBSUB_TOPIC)


def publish_message(data: dict):
    """Publishes a JSON message to Pub/Sub."""
    try:
        message_data = json.dumps(data).encode("utf-8")
        future = publisher.publish(topic_path, message_data)
        result_id = future.result()
        print(f"Published {data.get('message_type', 'unknown')} message ID: {result_id}")
    except Exception as e:
        print(f"Error publishing message: {e}")


def fetch_stock_quote():
    """Fetches live stock price data from Finnhub."""
    try:
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={STOCK_SYMBOL}&token={FINNHUB_API_KEY}"
        resp = requests.get(quote_url, timeout=10)
        resp.raise_for_status()
        quote = resp.json()
        quote["message_type"] = "stock_price"
        quote["symbol"] = STOCK_SYMBOL
        # Use US Eastern Time in ISO 8601 string format
        quote["fetched_at"] = datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%dT%H:%M:%SZ")
        return quote
    except Exception as e:
        print(f"Error fetching stock quote: {e}")
        return None
    
def main():
    print(f"Publishing stock price data for symbol '{STOCK_SYMBOL}' every {PUBLISH_INTERVAL_SEC} seconds to Pub/Sub topic '{PUBSUB_TOPIC}'")
    while True:
        stock_quote = fetch_stock_quote()
        if stock_quote:
            publish_message(stock_quote)
        time.sleep(PUBLISH_INTERVAL_SEC)


if __name__ == "__main__":
    main()