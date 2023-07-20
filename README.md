# Katulu FL Suite

---
ℹ️ The Katulu FL Suite has been deprecated and will no longer be maintained. The new version of our product is a massive leap.
We redesigned large parts of the system and developed it into a new platform better fit for production use cases with unique features to bridge data barriers for new insights from otherwise inaccessible data.

Highlights:
- Unified Data Catalog: An overview of all data available via connected agents - no matter the source.
- Portable Data Pipelines: Streamline your data workflow and unlock the full potential of federated learning.
- Run Anywhere: Our lightweight Agents run on Windows, Linux, MacOS, and many more.
- Cohorts: Automatically cluster results to not mishmash everything into average results but get the best for each cohort. 

Check out katulu.io to learn more about our platform!

---

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

### Local kubernetes cluster

For instructions how to spin up a local kubernetes environment please see the [develop README.md](develop/README.md)
