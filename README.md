# Katulu FL Suite

## Development

This project makes use of submodules to include external components like kubeflow to resolve latency issues with other means of inclusion like external kustomize resources.

Clone this repository including all submodules using the following command:

```sh
git clone --recursive git@github.com:katulu-io/fl-suite.git

```

Already cloned without recursive options? Run the following command to initialize all the submodules.

```sh
git submodule update --init --recursive
```
