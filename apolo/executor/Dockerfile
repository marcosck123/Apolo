FROM python:3.13-slim
WORKDIR /app
COPY servidor.py .
USER 65534:65534
CMD ["python", "-I", "-B", "/app/servidor.py"]
