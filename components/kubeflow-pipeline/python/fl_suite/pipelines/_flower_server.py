from dataclasses import dataclass
from typing import List, Optional

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


@dataclass
class FLOutput:
    """Federated Learning Outputs, e.g ml-metadata, ml-models, etc."""

    name: str
    type: str
    cli_param: str


def flwr_server(
    container_image: str,
    entrypoint: Optional[List[str]] = None,
    fl_outputs: Optional[List[FLOutput]] = None,
    fl_params: Optional[FLParameters] = None,
) -> ContainerOp:
    """Component to run a Flower server for federated learning."""
    if fl_params is None:
        fl_params = FLParameters()

    if entrypoint is None:
        entrypoint = [
            "python3",
            "flwr_server",
        ]

    if fl_outputs is None:
        fl_outputs = [
            FLOutput("output_path", "Directory", "--output-path"),
            FLOutput("MLPipeline_ui_metadata", "UI metadata", "--metadata-output-path"),
        ]

    args = [
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
    ]

    outputs = []
    for fl_output in fl_outputs:
        outputs.append(OutputSpec(fl_output.name, type=fl_output.type))
        args.append(fl_output.cli_param)
        args.append(OutputPathPlaceholder(fl_output.name))

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
        outputs=outputs,
        implementation=ContainerImplementation(
            ContainerSpec(
                image="PLACEHOLDER",
                # Argo workflows version lower than v3.4 require the command (entrypoint in
                # Containerfile/Dockerfile).
                # Here we assume all flwr_server's respect the below entrypoint
                command=entrypoint,
                args=args,
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
    flwr_server_op.container.image = container_image

    return flwr_server_op


RESOURCE_ID = "{{workflow.name}}"
