FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY app/ /app/
EXPOSE 7860
ENV OLLAMA_BASE_URL=http://ollama:11434 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860
RUN chmod +x /app/run.sh
CMD ["/bin/bash", "/app/run.sh"]