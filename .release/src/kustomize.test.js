const yaml = require("js-yaml");
const kustomize = require("./kustomize");

describe("kustomize", () => {
  describe("getResourcePath", () => {
    it("resolves path", () => {
      expect(kustomize.getResourcePath("foo/bar/baz/kustomization.yaml", "../test")).toEqual("foo/bar/test");
    });

    it("ignores renaming", () => {
      expect(kustomize.getResourcePath("foo/bar/baz/kustomization.yaml", "coolio=../test")).toEqual("foo/bar/test");
    });
  });

  describe("getKustomizeResources", () => {
    it("extracts base resources", () => {
      const content = yaml.safeLoad(`
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base
  - ../../third-party
`);

      expect(
        kustomize.getKustomizeResources({
          filePath: "foo/bar/baz/kustomization.yaml",
          content,
        })
      ).toEqual(["foo/base", "foo/third-party"]);
    });

    it("extracts resources", () => {
      const content = yaml.safeLoad(`
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base
  - ../../third-party
`);

      expect(
        kustomize.getKustomizeResources({
          filePath: "foo/bar/baz/kustomization.yaml",
          content,
        })
      ).toEqual(["foo/base", "foo/third-party"]);
    });
  });

  describe("getCRDResources", () => {
    it("extracts CRD resources", () => {
      const content = yaml.safeLoad(`
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

crds:
  - crds/typeA.yaml
  - crds/typeB.yaml
`);

      expect(
        kustomize.getCRDResources({
          filePath: "foo/bar/baz/kustomization.yaml",
          content,
        })
      ).toEqual(["foo/bar/baz/crds/typeA.yaml", "foo/bar/baz/crds/typeB.yaml"]);
    });
  });

  describe("getConfigMapGeneratorResources", () => {
    it("extracts ConfigMapGenerator resources", () => {
      const content = yaml.safeLoad(`
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

# These labels are added to all configmaps and secrets.
generatorOptions:
  labels:
    fruit: apple

configMapGenerator:
- name: my-java-server-props
  behavior: merge
  files:
  - application.properties
  - more.properties
  - myFileName.ini=whatever.ini
- name: my-java-server-env-file-vars
  envs:
  - my-server-env.properties
  - more-server-props.env
- name: my-java-server-env-vars
  literals:
  - JAVA_HOME=/opt/java/jdk
  - JAVA_TOOL_OPTIONS=-agentlib:hprof
  options:
    disableNameSuffixHash: true
    labels:
      pet: dog
- name: dashboards
  files:
  - mydashboard.json
  options:
    annotations:
      dashboard: "1"
    labels:
      app.kubernetes.io/name: "app1"
`);

      expect(
        kustomize.getConfigMapGeneratorResources({
          filePath: "foo/bar/baz/kustomization.yaml",
          content,
        })
      ).toEqual([
        "foo/bar/baz/application.properties",
        "foo/bar/baz/more.properties",
        "foo/bar/baz/whatever.ini",
        "foo/bar/baz/my-server-env.properties",
        "foo/bar/baz/more-server-props.env",
        "foo/bar/baz/mydashboard.json",
      ]);
    });
  });

  describe("getOpenAPISchemaResources", () => {
    it("extracts OpenAPI Schema resources", () => {
      const content = yaml.safeLoad(`
resources:
 - my_resource.yaml
openapi:
  path: my_schema.json
`);

      expect(
        kustomize.getOpenAPISchemaResources({
          filePath: "foo/bar/baz/kustomization.yaml",
          content,
        })
      ).toEqual(["foo/bar/baz/my_schema.json"]);
    });
  });

  describe("getPatchResources", () => {
    it("extracts Patch resources", () => {
      const content = yaml.safeLoad(`
resources:
- deployment.yaml
patches:
  - path: add-label.patch.yaml
  - path: fix-version.patch.yaml
    target:
      labelSelector: "app.kubernetes.io/name=nginx"
`);

      expect(
        kustomize.getPatchResources({
          filePath: "foo/bar/baz/kustomization.yaml",
          content,
        })
      ).toEqual(["foo/bar/baz/add-label.patch.yaml", "foo/bar/baz/fix-version.patch.yaml"]);
    });
  });

  describe("getJson6902PatchResources", () => {
    it("extracts Json6902 patch resources", () => {
      const content = yaml.safeLoad(`
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

patchesJson6902:
- target:
    version: v1
    kind: Deployment
    name: my-deployment
  path: add_init_container.yaml
- target:
    version: v1
    kind: Service
    name: my-service
  path: add_service_annotation.yaml
`);

      expect(
        kustomize.getJson6902PatchResources({
          filePath: "foo/bar/baz/kustomization.yaml",
          content,
        })
      ).toEqual(["foo/bar/baz/add_init_container.yaml", "foo/bar/baz/add_service_annotation.yaml"]);
    });
  });

  describe("getStrategicMergeResources", () => {
    it("extracts StrategicMerge resources", () => {
      const content = yaml.safeLoad(`
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

patchesStrategicMerge:
- service_port_8888.yaml
- deployment_increase_replicas.yaml
- deployment_increase_memory.yaml
`);

      expect(
        kustomize.getStrategicMergeResources({
          filePath: "foo/bar/baz/kustomization.yaml",
          content,
        })
      ).toEqual([
        "foo/bar/baz/service_port_8888.yaml",
        "foo/bar/baz/deployment_increase_replicas.yaml",
        "foo/bar/baz/deployment_increase_memory.yaml",
      ]);
    });
  });

  describe("getReplacementResources", () => {
    it("extracts Replacemenr resources", () => {
      const content = yaml.safeLoad(`
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

replacements:
  - path: replacement.yaml
`);

      expect(
        kustomize.getReplacementResources({
          filePath: "foo/bar/kustomization.yaml",
          content,
        })
      ).toEqual(["foo/bar/replacement.yaml"]);
    });
  });

  describe("getSecretGeneratorResources", () => {
    it("extracts Replacemenr resources", () => {
      const content = yaml.safeLoad(`
secretGenerator:
- name: app-tls
  files:
  - secret/tls.crt
  - secret/tls.key
  type: "kubernetes.io/tls"
- name: app-tls-namespaced
  # you can define a namespace to generate
  # a secret in, defaults to: "default"
  namespace: apps
  files:
  - tls.crt=catsecret/tls.crt
  - tls.key=catsecret/tls.key
  type: "kubernetes.io/tls"
- name: env_file_secret
  envs:
  - env.txt
  type: Opaque
- name: secret-with-annotation
  files:
  - app-config.yaml
  type: Opaque
  options:
    annotations:
      app_config: "true"
    labels:
      app.kubernetes.io/name: "app2"
`);

      expect(
        kustomize.getSecretGeneratorResources({
          filePath: "foo/bar/kustomization.yaml",
          content,
        })
      ).toEqual([
        "foo/bar/secret/tls.crt",
        "foo/bar/secret/tls.key",
        "foo/bar/catsecret/tls.crt",
        "foo/bar/catsecret/tls.key",
        "foo/bar/env.txt",
        "foo/bar/app-config.yaml",
      ]);
    });
  });
});
