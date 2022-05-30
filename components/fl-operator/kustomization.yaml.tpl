apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- kustomize/default
commonLabels:
  app: fl-operator
  app.kubernetes.io/component: fl-operator
  app.kubernetes.io/name: fl-operator
  kustomize.component: fl-operator
