FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py vision.py db.py auth.py .
COPY scripts ./scripts
ENV MQTT_HOST=mosquitto MQTT_PORT=1883 MQTT_TOPIC=agrivision/#
ENV DATABASE_URL=postgresql+psycopg://agrivision:agrivision@postgres:5432/agrivision
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
