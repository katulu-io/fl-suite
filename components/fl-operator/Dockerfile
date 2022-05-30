# Use distroless as minimal base image to package the manager binary
# Refer to https://github.com/GoogleContainerTools/distroless for more details
FROM gcr.io/distroless/static:nonroot

LABEL org.opencontainers.image.source https://github.com/katulu-io/fl-suite

WORKDIR /
COPY ./bin/manager .
COPY deployment /deployment

USER 65532:65532

ENTRYPOINT ["/manager"]
