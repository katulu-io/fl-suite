# FL Operator

Kubernetes operator in charge of scheduling federated learning clients (e.g flower-clients) on-demand based on running
fl-suite workflows.

## Development

This project follows the [operator-sdk project layout](https://sdk.operatorframework.io/docs/overview/project-layout/#operator-sdk-project-layout).

### Create a new API

The `operator-sdk` is used to generate new APIs. For installation instructions check the [documentation](https://sdk.operatorframework.io/docs/installation/).

To create a new API with resources and controllers use the following command:

```shell
# Replace $KIND_NAME with the new API name
operator-sdk create api --verbose --group fl --version v1alpha1 --kind $KIND_NAME --resource --controller
```
