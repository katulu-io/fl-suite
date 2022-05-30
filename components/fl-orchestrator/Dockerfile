# hadolint ignore=DL3006
FROM gcr.io/distroless/static-debian11

LABEL org.opencontainers.image.source https://github.com/katulu-io/fl-suite

COPY ./dist/fl-orchestrator /

ENTRYPOINT ["/fl-orchestrator"]
