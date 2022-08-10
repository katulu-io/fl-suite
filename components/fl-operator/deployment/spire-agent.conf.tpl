agent {
  data_dir          = "/run/spire"
  log_level         = "DEBUG"
  server_address    = "{{.ServerAddress}}"
  server_port       = "{{.ServerPort}}"
  socket_path       = "/run/spire/sockets/agent.sock"
  # TODO: Figure out how to not do an insecure bootstrap
  insecure_bootstrap = true
  trust_domain      = "{{.TrustDomain}}"
  join_token        = "{{.JoinToken}}"
}

plugins {
  NodeAttestor "join_token" {
  }

  KeyManager "memory" {
    plugin_data {
    }
  }

  WorkloadAttestor "k8s" {
    plugin_data {
      skip_kubelet_verification = {{.SkipKubeletVerification}}
    }
  }
}
