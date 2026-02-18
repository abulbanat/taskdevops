FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app/main.py /app/main.py

EXPOSE 8080

ENV PORT=8080

CMD ["python", "/app/main.py"]
