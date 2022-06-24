FROM python:3.10

LABEL org.opencontainers.image.source https://github.com/katulu-io/fl-suite

COPY requirements.txt /pipelines/
RUN python3 -m pip install --no-cache-dir -r /pipelines/requirements.txt && \
    rm /pipelines/requirements.txt

COPY flwr_analytics_client /pipelines/component/flwr_analytics_client

ENV PYTHONPATH "${PYTHONPATH}:/pipelines/component"

ENTRYPOINT [ "python3", "-m", "flwr_analytics_client" ]
