FROM quay.io/buildah/stable:v1.23.1

LABEL org.opencontainers.image.source https://github.com/katulu-io/fl-suite

# hadolint ignore=DL3041
RUN dnf install -y jq && dnf clean all

COPY build.sh /

ENTRYPOINT [ "/build.sh" ]
