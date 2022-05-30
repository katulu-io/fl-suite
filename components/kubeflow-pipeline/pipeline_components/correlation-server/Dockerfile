FROM python:3.10

LABEL org.opencontainers.image.source https://github.com/katulu-io/fl-suite

COPY requirements.txt /pipelines/component/
RUN python3 -m pip install --no-cache-dir -r /pipelines/component/requirements.txt && \
    rm /pipelines/component/requirements.txt

# The folder has to be named 'flwr_server' because
# the entrypoint will have to be overwritten for pipelines
# and our pipelines assume this folder name.
COPY flwr_correlation_server /pipelines/component/flwr_server

ENTRYPOINT [ "python3", "/pipelines/component/flwr_server" ]
