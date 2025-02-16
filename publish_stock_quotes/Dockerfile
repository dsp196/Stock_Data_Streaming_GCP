FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY Publish_stock_producer.py /app

CMD ["python", "Publish_stock_producer_time.py"]
