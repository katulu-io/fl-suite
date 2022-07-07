apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: katulu-fl
resources:
- kustomize
commonLabels:
  app: jupyter-notebook
  app.kubernetes.io/component: jupyter-notebook
  app.kubernetes.io/name: jupyter-notebook
  kustomize.component: jupyter-notebook
