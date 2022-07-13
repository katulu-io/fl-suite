# --- Build the frontend kubeflow library ---
FROM node:16.13.1 as frontend-kubeflow-lib

WORKDIR /src

ENV NG_CLI_ANALYTICS "ci"
COPY ./vendor/kubeflow/components/crud-web-apps/common/frontend/kubeflow-common-lib/package.json ./
COPY ./vendor/kubeflow/components/crud-web-apps/common/frontend/kubeflow-common-lib/package-lock.json ./
RUN npm ci

COPY ./vendor/kubeflow/components/crud-web-apps/common/frontend/kubeflow-common-lib/projects ./projects
COPY ./vendor/kubeflow/components/crud-web-apps/common/frontend/kubeflow-common-lib/angular.json .
COPY ./vendor/kubeflow/components/crud-web-apps/common/frontend/kubeflow-common-lib/tsconfig.json .
RUN npm run build

# --- Build the frontend ---
FROM node:16.13.1-buster-slim as frontend

WORKDIR /src

COPY ./edge-identity/frontend/package.json ./
COPY ./edge-identity/frontend/package-lock.json ./
COPY ./edge-identity/frontend/tsconfig.json ./
COPY ./edge-identity/frontend/tsconfig.app.json ./
COPY ./edge-identity/frontend/tsconfig.spec.json ./
COPY ./edge-identity/frontend/angular.json ./
COPY ./edge-identity/frontend/src ./src

ENV NG_CLI_ANALYTICS "ci"
RUN npm ci
COPY --from=frontend-kubeflow-lib /src/dist/kubeflow/ ./node_modules/kubeflow/

RUN npm run build -- --output-path=./dist/default --configuration=production

FROM python:3.9-slim-buster as webapp

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

# Install poetry
ENV POETRY_HOME "/opt/poetry"
ENV PATH $POETRY_HOME/bin:$PATH
ENV POETRY_VIRTUALENVS_CREATE "false"
# hadolint ignore=DL3008
RUN url="https://install.python-poetry.org"; \
    apt-get update -qq; \
    apt-get install -qq -y --no-install-recommends wget; \
    \
    wget -q -O- "$url" | POETRY_VERSION=1.1.13 python3 -; \
    poetry --version; \
    rm -rf /var/lib/apt/lists/*;

WORKDIR /app/src

COPY ./edge-identity/backend/pyproject.toml .
COPY ./edge-identity/backend/poetry.lock .

RUN mkdir /vendor
COPY ./vendor/kubeflow /vendor/kubeflow

RUN poetry install

COPY ./edge-identity/backend/spire/ ./spire
COPY ./edge-identity/backend/apps/ ./apps
COPY ./edge-identity/backend/entrypoint.py .

COPY --from=frontend /src/dist/default/ /app/src/apps/default/static/

ENTRYPOINT ["/bin/bash", "-c", "FLASK_APP=apps.default flask init-db && gunicorn -w 3 --bind 0.0.0.0:5000 --access-logfile - entrypoint:app"]
