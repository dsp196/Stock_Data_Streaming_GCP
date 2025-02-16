import os
import time
import json
import requests
from google.cloud import pubsub_v1
from datetime import datetime
import pytz
import finnhub



FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
GCP_PROJECT = os.getenv("GCP_PROJECT")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC")

if not FINNHUB_API_KEY:
    raise ValueError("FINNHUB_API_KEY is not set in environment variables!")
if not GCP_PROJECT:
    raise ValueError("GCP_PROJECT is not set in environment variables!")
if not PUBSUB_TOPIC:
    raise ValueError("PUBSUB_TOPIC is not set in environment variables!")





STOCK_SYMBOL = "AAPL"
PUBLISH_INTERVAL_SEC = 60
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
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



def fetch_and_publish_company_profile():
    """
    Fetch company profile once and publish to the same Pub/Sub topic.
    """
    try:
        profile = finnhub_client.company_profile2(symbol=STOCK_SYMBOL)
        if profile:
            profile["message_type"] = "company_info"
            profile["symbol"] = STOCK_SYMBOL
            # record local time in US/Eastern
            profile["fetched_at"] = datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%dT%H:%M:%SZ")
            publish_message(profile)
        else:
            print("No company profile data returned.")
    except Exception as e:
        print(f"Error fetching company profile: {e}")


def main():
    print(f"Publishing to Pub/Sub topic '{PUBSUB_TOPIC}' in project '{GCP_PROJECT}'")
    # print(f"Fetching Finnhub data for symbol '{STOCK_SYMBOL}' every {PUBLISH_INTERVAL_SEC} seconds")

    # 1) Publish company-related data (ONCE at startup)
    fetch_and_publish_company_profile()

    # 2) Continuously publish stock price data
    # while True:
    #     fetch_and_publish_stock_quote()
    #     time.sleep(PUBLISH_INTERVAL_SEC)



if __name__ == "__main__":
    main()