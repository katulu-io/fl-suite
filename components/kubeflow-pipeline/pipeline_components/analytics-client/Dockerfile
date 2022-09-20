FROM python:3.10

LABEL org.opencontainers.image.source https://github.com/katulu-io/fl-suite

COPY requirements.txt /app/
RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt && \
    rm /app/requirements.txt

COPY flwr_analytics_client /app/flwr_analytics_client/
COPY main.py /app/

ENV PYTHONPATH="${PYTHONPATH}:/app"

ENTRYPOINT [ "python3", "/app/main.py" ]
