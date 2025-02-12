FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY Company_info_producer.py /app

CMD ["python", "Company_info_producer.py"]
