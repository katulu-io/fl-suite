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
from kfp.dsl import ContainerOp

from ._flower_infrastructure import add_envoy_proxy


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
    add_envoy_proxy(flwr_server_op)

    return flwr_server_op


RESOURCE_ID = "{{workflow.name}}"
