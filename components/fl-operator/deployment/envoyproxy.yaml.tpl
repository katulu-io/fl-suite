---
node:
  id: {{.SourceName}}
  cluster: local-k8s

admin:
  address:
    socket_address:
      address: 0.0.0.0
      port_value: 9901

static_resources:
  listeners:
    - name: http-listener
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 9080
      filter_chains:
        filters:
          - name: envoy.filters.network.http_connection_manager
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
              set_current_client_cert_details:
                uri: true
              codec_type: AUTO
              stat_prefix: http-listener
              route_config:
                name: {{.DestinationName}}-envoyproxy
                virtual_hosts:
                  - name: {{.DestinationName}}-envoyproxy
                    domains: ["*"]
                    routes:
                      - match:
                          prefix: "/"
                        route:
                          cluster: {{.DestinationName}}-envoyproxy
              access_log:
                - name: file
                  typed_config:
                    "@type": type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog
                    path: /dev/stdout
              http_filters:
                - name: envoy.filters.http.router
  clusters:
    - name: spire_agent
      connect_timeout: 1s
      type: STATIC
      lb_policy: ROUND_ROBIN
      typed_extension_protocol_options:
        envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
          "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
          explicit_http_config:
            http2_protocol_options: {}
      load_assignment:
        cluster_name: spire_agent
        endpoints:
          - lb_endpoints:
            - endpoint:
                address:
                  pipe:
                    path: /run/spire/sockets/agent.sock
    - name: {{.DestinationName}}-envoyproxy
      connect_timeout: 1s
      type: STRICT_DNS
      lb_policy: ROUND_ROBIN
      typed_extension_protocol_options:
        envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
          "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
          explicit_http_config:
            http2_protocol_options: {}
      load_assignment:
        cluster_name: {{.DestinationName}}-envoyproxy
        endpoints:
          - lb_endpoints:
            - endpoint:
                address:
                  socket_address:
                    address: {{.EndpointAddress}}
                    port_value: {{.EndpointPort}}
      transport_socket:
        name: envoy.transport_sockets.tls
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.UpstreamTlsContext
          sni: {{.EndpointSNI}}
          common_tls_context:
            tls_certificate_sds_secret_configs:
              - name: spiffe://katulu.io/{{.SourceName}}
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
                  - exact: spiffe://katulu.io/{{.DestinationName}}
              validation_context_sds_secret_config:
                name: spiffe://katulu.io
                sds_config:
                  resource_api_version: V3
                  api_config_source:
                    api_type: GRPC
                    transport_api_version: V3
                    grpc_services:
                      envoy_grpc:
                        cluster_name: spire_agent # Must be specified in "clusters"
