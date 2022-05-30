FROM python:3.10

LABEL org.opencontainers.image.source https://github.com/katulu-io/fl-suite

COPY requirements.txt /pipelines/
RUN python3 -m pip install --no-cache-dir -r /pipelines/requirements.txt && \
    rm /pipelines/requirements.txt

COPY flwr_correlation_client /pipelines/component/flwr_correlation_client

ENTRYPOINT [ "python3", "/pipelines/component/flwr_correlation_client" ]
