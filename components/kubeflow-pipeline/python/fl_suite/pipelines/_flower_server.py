from dataclasses import dataclass
from typing import Optional

from kfp.components import load_component
from kfp.components._structures import (
    ComponentSpec,
    ContainerImplementation,
    ContainerSpec,
    InputSpec,
    InputValuePlaceholder,
    MetadataSpec,
    OutputPathPlaceholder,
    OutputSpec,
)
from kfp.dsl import ContainerOp, Sidecar
from kubernetes import client as k8s_client

from ._flower_infrastructure import ENVOYPROXY_NAME


@dataclass
class FLParameters:
    """Federated Learning Parameters."""

    num_rounds: int = 3
    num_local_rounds: int = 1
    min_available_clients: int = 2
    min_fit_clients: int = 2
    min_eval_clients: int = 2


def flwr_server(
    server_image: str,
    fl_params: Optional[FLParameters] = None,
) -> ContainerOp:
    """Component to run a Flower server for federated learning."""
    if fl_params is None:
        fl_params = FLParameters()

    flwr_server_spec = ComponentSpec(
        name="Flower Server",
        description="Start a Flower server for Federated Learning",
        metadata=MetadataSpec(
            labels={
                "katulu/fl-server": "flower-server",
            },
        ),
        inputs=[
            InputSpec("num_rounds", type="Integer"),
            InputSpec("num_local_rounds", type="Integer"),
            InputSpec("min_available_clients", type="Integer"),
            InputSpec("min_fit_clients", type="Integer"),
            InputSpec("min_eval_clients", type="Integer"),
        ],
        outputs=[
            OutputSpec("output_path", type="Directory"),
            OutputSpec("MLPipeline_ui_metadata", type="UI metadata"),
        ],
        implementation=ContainerImplementation(
            ContainerSpec(
                image=server_image,
                command=[
                    "python3",
                    "/pipelines/component/flwr_server",
                    "--num-rounds",
                    InputValuePlaceholder("num_rounds"),
                    "--num-local-rounds",
                    InputValuePlaceholder("num_local_rounds"),
                    "--min-available-clients",
                    InputValuePlaceholder("min_available_clients"),
                    "--min-fit-clients",
                    InputValuePlaceholder("min_fit_clients"),
                    "--min-eval-clients",
                    InputValuePlaceholder("min_eval_clients"),
                    "--output-path",
                    OutputPathPlaceholder("output_path"),
                    "--metadata-output-path",
                    OutputPathPlaceholder("MLPipeline_ui_metadata"),
                ],
            )
        ),
    )
    component = load_component(component_spec=flwr_server_spec)
    # pylint: disable-next=not-callable
    flwr_server_op: ContainerOp = component(
        fl_params.num_rounds,
        fl_params.num_local_rounds,
        fl_params.min_available_clients,
        fl_params.min_fit_clients,
        fl_params.min_eval_clients,
    )
    flwr_server_op.enable_caching = False

    flwr_server_op.add_sidecar(
        Sidecar(
            name="envoyproxy",
            image="envoyproxy/envoy:v1.20-latest",
            command=["/docker-entrypoint.sh"],
            args=[
                "-l",
                "debug",
                "--local-address-ip-version",
                "v4",
                "-c",
                "/run/envoy/envoy.yaml",
                "--base-id",
                "1",
            ],
            volume_mounts=[
                k8s_client.V1VolumeMount(
                    name="envoy-config", mount_path="/run/envoy", read_only=True
                ),
                k8s_client.V1VolumeMount(
                    name="spire-agent-socket",
                    mount_path="/run/spire/sockets",
                    read_only=True,
                ),
            ],
        )
    )
    flwr_server_op.add_volume(
        k8s_client.V1Volume(
            name="envoy-config",
            config_map=k8s_client.V1ConfigMapVolumeSource(name=ENVOYPROXY_NAME),
        )
    )
    flwr_server_op.add_volume(
        k8s_client.V1Volume(
            name="spire-agent-socket",
            host_path=k8s_client.V1HostPathVolumeSource(
                path="/run/spire/sockets", type="DirectoryOrCreate"
            ),
        )
    )
    flwr_server_op.add_pod_label("spire-workload", RESOURCE_ID)

    return flwr_server_op


RESOURCE_ID = "{{workflow.name}}"
