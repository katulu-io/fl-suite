FROM buildpack-deps:bullseye-scm

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

LABEL org.opencontainers.image.source https://github.com/katulu-io/fl-suite

# apt install Buildah, docker, make, unzip, plus additional packages needed for cgo
# hadolint ignore=DL3008
RUN echo 'deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/Debian_11/ /' > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list; \
    # TODO: Embed key instead of downloading.
    wget -O Release.key https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/Debian_11/Release.key --progress=dot:giga; \
    apt-key add - < Release.key; \
    rm Release.key; \
    \
    echo 'deb http://ppa.launchpad.net/ansible/ansible/ubuntu trusty main' >> /etc/apt/sources.list; \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367; \
    \
    apt-get update -qq; \
    apt-get install -qq -y --no-install-recommends \
    g++ \
    gcc \
    libc6-dev \
    make \
    pkg-config \
    \
    unzip \
    jq \
    python3-venv \
    python3-setuptools \
    python3-pip \
    python-is-python3 \
    buildah \
    \
    docker.io \
    \
    chromium && \
    \
    rm -rf /var/lib/apt/lists/*; \
    \
    buildah --version;

# Set up env to note that buildah is not starting with user namespace and default to isolate the filesystem with chroot.
ENV BUILDAH_ISOLATION=chroot

# Install go (adapted from https://github.com/docker-library/golang/blob/master/1.16/buster/Dockerfile)
ENV PATH /usr/local/go/bin:$PATH
# hadolint ignore=SC2041
RUN url='https://go.dev/dl/go1.18.3.linux-amd64.tar.gz'; \
    sha256='956f8507b302ab0bb747613695cdae10af99bbd39a90cae522b7c0302cc27245'; \
    \
    wget -O go.tgz.asc "$url.asc" --progress=dot:giga; \
    wget -O go.tgz "$url" --progress=dot:giga; \
    echo "$sha256 *go.tgz" | sha256sum --strict --check -; \
    \
    # https://github.com/golang/go/issues/14739#issuecomment-324767697
    GNUPGHOME="$(mktemp -d)"; \
    export GNUPGHOME; \
    for key in 'EB4C1BFD4F042F6DDDCCEC917721F63BD38B4796'; do \
    gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$key"; \
    done; \
    gpg --batch --verify go.tgz.asc go.tgz; \
    gpgconf --kill all; \
    rm -rf "$GNUPGHOME" go.tgz.asc; \
    \
    tar -C /usr/local -xzf go.tgz; \
    rm go.tgz; \
    \
    go version

ENV GOPATH /go
ENV PATH $GOPATH/bin:$PATH
RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" && chmod -R 777 "$GOPATH"

# Install golangci-lint (https://github.com/golangci/golangci-lint/releases)
RUN url="https://github.com/golangci/golangci-lint/releases/download/v1.45.2/golangci-lint-1.45.2-linux-amd64.tar.gz"; \
    sha256="595ad6c6dade4c064351bc309f411703e457f8ffbb7a1806b3d8ee713333427f"; \
    wget -O golangci-lint.tgz "$url" --progress=dot:giga; \
    echo "$sha256 *golangci-lint.tgz" | sha256sum --strict --check -; \
    \
    tar -C /usr/local/bin -xzf golangci-lint.tgz --strip-components=1 golangci-lint-1.45.2-linux-amd64/golangci-lint; \
    chmod +x /usr/local/bin/golangci-lint; \
    rm golangci-lint.tgz; \
    \
    golangci-lint version

# This env is used by tools like karmna (teset runner) to launch chromium for browser testing.
ENV CHROME_BIN=/usr/bin/chromium

# Install node and yarn
RUN url="https://nodejs.org/dist/v16.13.1/node-v16.13.1-linux-x64.tar.gz"; \
    sha256='5f80197d654fd0b749cdeddf1f07a5eac1fcf6b423a00ffc8f2d3bea9c6dc8d1'; \
    \
    wget -O node.tgz "$url" --progress=dot:giga; \
    echo "$sha256 *node.tgz" | sha256sum --strict --check -; \
    \
    tar -C /usr/local -xzf node.tgz --strip-components=1; \
    rm node.tgz; \
    \
    node --version; \
    \
    corepack enable; \
    corepack prepare yarn@3.1.1 --activate;

# Install hadolint (https://github.com/hadolint/hadolint/releases)
RUN url='https://github.com/hadolint/hadolint/releases/download/v2.8.0/hadolint-Linux-x86_64'; \
    sha256='9dfc155139a1e1e9b3b28f3de9907736b9dfe7cead1c3a0ae7ff0158f3191674'; \
    \
    wget -O hadolint "$url" --progress=dot:giga; \
    echo "$sha256 *hadolint" | sha256sum --strict --check -; \
    \
    chmod +x hadolint; \
    mv hadolint /usr/local/bin; \
    \
    hadolint --version

# Install kubectl (https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
RUN kubectl_version="1.23.1"; \
    url="https://dl.k8s.io/release/v${kubectl_version}/bin/linux/amd64/kubectl"; \
    sha256="156fd5e7ebbedf3c482fd274089ad75a448b04cf42bc53f370e4e4ea628f705e"; \
    \
    wget -O kubectl "$url" --progress=dot:giga; \
    echo "$sha256 kubectl" | sha256sum --strict --check -; \
    \
    mv kubectl /usr/local/bin; \
    chmod +x /usr/local/bin/kubectl; \
    \
    kubectl version --client=true

# Install kustomize
RUN url="https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv4.4.1/kustomize_v4.4.1_linux_amd64.tar.gz"; \
    sha256="2d5927efec40ba32a121c49f6df9955b8b8a296ef1dec4515a46fc84df158798"; \
    \
    wget -O kustomize.tgz "$url" --progress=dot:giga; \
    echo "$sha256 kustomize.tgz" | sha256sum --strict --check -; \
    \
    tar -C /usr/local/bin -xzf kustomize.tgz; \
    rm kustomize.tgz; \
    \
    kustomize version;

# Install poetry
ENV POETRY_HOME "/opt/poetry"
ENV PATH $POETRY_HOME/bin:$PATH
RUN url="https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py"; \
    \
    wget -q -O- "$url" | POETRY_VERSION=1.1.14 python3 -; \
    poetry --version;

# Install kind
RUN url="https://kind.sigs.k8s.io/dl/v0.13.0/kind-linux-amd64"; \
    sha256="c80c6d1013337cbbe226c2eda0a3dc2d75af16e5fa8af4ce3fc9fedcf1f9d2dc"; \
    \
    wget -O kind "$url" --progress=dot:giga; \
    echo "$sha256 kind" | sha256sum --strict --check -; \
    \
    chmod +x kind; \
    mv kind /usr/local/bin; \
    \
    kind version;

WORKDIR /workspace

CMD [ "/bin/bash" ]
