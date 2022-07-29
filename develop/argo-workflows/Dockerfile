FROM python:3.10
RUN python -m pip install --no-cache-dir tensorflow flwr
COPY main.py /app/
ENTRYPOINT [ "python", "/app/main.py" ]
