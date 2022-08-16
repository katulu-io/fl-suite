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
RUN url='https://go.dev/dl/go1.19.linux-amd64.tar.gz'; \
    sha256='464b6b66591f6cf055bc5df90a9750bf5fbc9d038722bb84a9d56a2bea974be6'; \
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
RUN url="https://github.com/golangci/golangci-lint/releases/download/v1.48.0/golangci-lint-1.48.0-linux-amd64.tar.gz"; \
    sha256="127c5c9d47cf3a3cf4128815dea1d9623d57a83a22005e91b986b0cbceb09233"; \
    wget -O golangci-lint.tgz "$url" --progress=dot:giga; \
    echo "$sha256 *golangci-lint.tgz" | sha256sum --strict --check -; \
    \
    tar -C /usr/local/bin -xzf golangci-lint.tgz --strip-components=1 golangci-lint-1.48.0-linux-amd64/golangci-lint; \
    chmod +x /usr/local/bin/golangci-lint; \
    rm golangci-lint.tgz; \
    \
    golangci-lint version

# This env is used by tools like karmna (teset runner) to launch chromium for browser testing.
ENV CHROME_BIN=/usr/bin/chromium

# Install node and yarn
RUN url="https://nodejs.org/dist/v16.16.0/node-v16.16.0-linux-x64.tar.gz"; \
    sha256='c85b16d1a4c259d01be7111ecb0361260627e4fc245004a920521eacb28e50df'; \
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
    corepack prepare yarn@3.2.2 --activate;

# Install hadolint (https://github.com/hadolint/hadolint/releases)
RUN url='https://github.com/hadolint/hadolint/releases/download/v2.10.0/hadolint-Linux-x86_64'; \
    sha256='8ee6ff537341681f9e91bae2d5da451b15c575691e33980893732d866d3cefc4'; \
    \
    wget -O hadolint "$url" --progress=dot:giga; \
    echo "$sha256 *hadolint" | sha256sum --strict --check -; \
    \
    chmod +x hadolint; \
    mv hadolint /usr/local/bin; \
    \
    hadolint --version

# Install kubectl (https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
RUN kubectl_version="1.24.3"; \
    url="https://dl.k8s.io/release/v${kubectl_version}/bin/linux/amd64/kubectl"; \
    sha256="8a45348bdaf81d46caf1706c8bf95b3f431150554f47d444ffde89e8cdd712c1"; \
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
RUN url="https://kind.sigs.k8s.io/dl/v0.14.0/kind-linux-amd64"; \
    sha256="af5e8331f2165feab52ec2ae07c427c7b66f4ad044d09f253004a20252524c8b"; \
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
