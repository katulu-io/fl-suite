# Edge identity service

## Local development

### Build the common (kubeflow) frontend library
```shell
# build the common library
cd $FL_SUITE_ROOT_DIR/components/vendor/kubeflow/components/crud-web-apps/common/frontend/kubeflow-common-lib
npm i
npm run build
cd dist/kubeflow
npm link
```

### Build the frontend

```shell
cd $FL_SUITE_ROOT_DIR/components/edge-identity/frontend
npm i
npm link kubeflow
npm run build:watch
```

### Run the backend service

The backend service serves the frontend (static files).

```shell
cd $FL_SUITE_ROOT_DIR/components/edge-identity
make run
```
