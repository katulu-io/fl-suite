from kfp.components import load_component
from kfp.components._structures import (
    ComponentSpec,
    ContainerImplementation,
    ContainerSpec,
    MetadataSpec,
    OutputPathPlaceholder,
    OutputSpec,
)
from kfp.v2.dsl import ContainerOp


def cleanup_kubernetes_resources() -> ContainerOp:
    """Component to cleanup Kubernetes resources that were needed for federated learning."""
    cleanup_kubernetes_resources_spec = ComponentSpec(
        name="Cleanup Flower Server Infrastructure",
        implementation=ContainerImplementation(
            ContainerSpec(
                image="gcr.io/cloud-builders/kubectl",
                command=["sh", "-c"],
                args=[
                    "kubectl -n katulu-fl delete --ignore-not-found=true virtualservice,svc,cm "
                    f"-l workflows.argoproj.io/workflow={RESOURCE_ID}"
                ],
            )
        ),
    )
    component = load_component(component_spec=cleanup_kubernetes_resources_spec)
    # pylint: disable-next=not-callable
    cleanup_kubernetes_resources_op: ContainerOp = component()

    return cleanup_kubernetes_resources_op


def setup_kubernetes_resources() -> ContainerOp:
    """Component to create Kubernetes resources necessary for Federated Learning."""
    setup_kubernetes_resources_spec = ComponentSpec(
        name="Setup Flower Server Infrastructure",
        metadata=MetadataSpec(
            labels={"katulu/fl-server": "infrastructure"},
        ),
        outputs=[
            OutputSpec(name="flower_server_sni", type="Path"),
        ],
        implementation=ContainerImplementation(
            ContainerSpec(
                image="gcr.io/cloud-builders/kubectl",
                command=["sh", "-c"],
                args=[
                    f"kubectl apply -f - << EOF && "
                    f'mkdir -p $(dirname "$0") && '
                    f'kubectl -n katulu-fl get virtualservice "{RESOURCE_ID}" '
                    f'-o jsonpath="{{ .spec.hosts[0] }}" > "$0" '
                    f"{INFRASTRUCTURE_YAML}"
                    "EOF",
                    OutputPathPlaceholder("flower_server_sni"),
                ],
            )
        ),
    )
    component = load_component(component_spec=setup_kubernetes_resources_spec)
    # pylint: disable-next=not-callable
    setup_kubernetes_resources_op: ContainerOp = component()
    setup_kubernetes_resources_op.enable_caching = False

    return setup_kubernetes_resources_op


RESOURCE_ID = "{{workflow.name}}"
ENVOYPROXY_NAME = f"{RESOURCE_ID}-envoyproxy"
FLOWER_SERVER_NAME = f"{RESOURCE_ID}-flower-server"


INFRASTRUCTURE_YAML = f"""
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: "{RESOURCE_ID}"
  namespace: katulu-fl
  labels:
    workflows.argoproj.io/workflow: {RESOURCE_ID}
spec:
  gateways:
    - flower-server-envoyproxy
  hosts:
    - "{RESOURCE_ID}.fl.katulu.io"
  tls:
    - match:
        - port: 443
          sniHosts:
            - "{RESOURCE_ID}.fl.katulu.io"
      route:
        - destination:
            host: "{ENVOYPROXY_NAME}"
            port:
              number: 9001

---
apiVersion: v1
kind: Service
metadata:
  name: "{FLOWER_SERVER_NAME}"
  namespace: katulu-fl
  labels:
    workflows.argoproj.io/workflow: {RESOURCE_ID}
spec:
  selector:
    spire-workload: "{RESOURCE_ID}"
  ports:
    - name: grpc
      protocol: TCP
      port: 8080
      targetPort: 8080

---
apiVersion: v1
kind: Service
metadata:
  name: "{ENVOYPROXY_NAME}"
  namespace: katulu-fl
  labels:
    workflows.argoproj.io/workflow: {RESOURCE_ID}
spec:
  selector:
    spire-workload: "{RESOURCE_ID}"
  ports:
    - name: grpc
      port: 9001
      targetPort: 9001
      protocol: TCP

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: "{ENVOYPROXY_NAME}"
  namespace: katulu-fl
  labels:
    workflows.argoproj.io/workflow: {RESOURCE_ID}
data:
  envoy.yaml: |
    ---
    node:
      id: "{RESOURCE_ID}"
      cluster: local-k8s
    static_resources:
      listeners:
        - name: local_service
          address:
            socket_address:
              address: 0.0.0.0
              port_value: 9001
          filter_chains:
            - filters:
              - name: envoy.filters.network.http_connection_manager
                typed_config:
                  "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                  set_current_client_cert_details:
                    uri: true
                  codec_type: AUTO
                  stat_prefix: tls-http-listener
                  access_log:
                    - name: envoy.file_access_log
                      config:
                        path: "/dev/stdout"
                  route_config:
                    name: local_route
                    virtual_hosts:
                      - name: flower-server
                        domains:
                          - "*"
                        routes:
                          - match:
                              prefix: "/"
                            route:
                              cluster: flower-server
                  access_log:
                    - name: file
                      typed_config:
                        "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
                        path: /dev/stdout
                  http_filters:
                    - name: envoy.filters.http.router
              transport_socket:
                name: envoy.transport_sockets.tls
                typed_config:
                  "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
                  common_tls_context:
                    tls_certificate_sds_secret_configs:
                      - name: spiffe://katulu.io/{RESOURCE_ID}
                        sds_config:
                          resource_api_version: V3
                          api_config_source:
                            api_type: GRPC
                            transport_api_version: V3
                            grpc_services:
                              envoy_grpc:
                                cluster_name: spire_agent
                    combined_validation_context:
                      default_validation_context:
                        match_subject_alt_names:
                          exact: spiffe://katulu.io/flower-client
                      validation_context_sds_secret_config:
                        name: spiffe://katulu.io
                        sds_config:
                          resource_api_version: V3
                          api_config_source:
                            api_type: GRPC
                            transport_api_version: V3
                            grpc_services:
                              envoy_grpc:
                                cluster_name: spire_agent
      clusters:
        - name: spire_agent
          connect_timeout: 1s
          type: STATIC
          lb_policy: ROUND_ROBIN
          typed_extension_protocol_options:
            envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
              "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
              explicit_http_config:
                http2_protocol_options: {{}}
          load_assignment:
            cluster_name: spire_agent
            endpoints:
              - lb_endpoints:
                - endpoint:
                    address:
                      pipe:
                        path: /run/spire/sockets/agent.sock
        - name: flower-server
          connect_timeout: 1s
          type: strict_dns
          typed_extension_protocol_options:
            envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
              "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
              explicit_http_config:
                http2_protocol_options: {{}}
          load_assignment:
            cluster_name: flower-server
            endpoints:
              - lb_endpoints:
                - endpoint:
                    address:
                      socket_address:
                        address: "{FLOWER_SERVER_NAME}"
                        port_value: 8080
"""  # noqa: E501
