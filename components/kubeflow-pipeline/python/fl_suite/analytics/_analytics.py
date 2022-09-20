import inspect
import itertools
import textwrap
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Iterable, Optional, Union

import numpy as np
from kfp.components import load_component
from kfp.components._structures import (
    ComponentSpec,
    ContainerImplementation,
    ContainerSpec,
    InputPathPlaceholder,
    InputSpec,
    InputValuePlaceholder,
    MetadataSpec,
    OutputPathPlaceholder,
    OutputSpec,
)
from kfp.dsl import ContainerOp

from .._version import __version__


def data(
    packages: Optional[Iterable[str]] = None,
) -> Callable[[Callable[[], np.ndarray]], Callable[[str, bool], ContainerOp]]:
    """Decorator for an analytics data provider.

    The data provided by this function is used to calculate federated correlation.
    On the client, certain properties of this data is extracted and sent to the server."""
    if packages is None:
        packages = []

    def _wrapped(func: Callable[[], np.ndarray]) -> Callable[[str, bool], ContainerOp]:
        func_code = textwrap.dedent(inspect.getsource(func))

        func_code_lines = func_code.split("\n")

        # Removing possible decorators (can be multiline) until the function
        # definition is found
        func_code_lines = list(
            itertools.dropwhile(lambda x: not x.startswith("def"), func_code_lines)
        )

        func_code = textwrap.dedent("\n".join(func_code_lines[1:]))
        func_code = (
            "import numpy as np\n\n"
            f"def data() -> np.ndarray:\n{textwrap.indent(func_code, '    ')}"
        )

        @wraps(func)
        def _inner(registry: str, verify_registry_tls: bool) -> ContainerOp:
            return prepare_analytics_client(func_code, packages, registry, verify_registry_tls)

        return _inner

    return _wrapped


def prepare_analytics_client(
    data_func: str,
    packages: Iterable[str],
    registry: str,
    _: bool,
) -> ContainerOp:
    """Instructions to build a client image for federated correlation."""
    analytics_client_base = f"{registry}/analytics-client:{__version__}"

    prepare_context_spec = ComponentSpec(
        name="Prepare build context",
        inputs=[
            InputSpec(name="pip_packages", type="String"),
            InputSpec(name="python_script", type="String"),
        ],
        outputs=[
            OutputSpec(name="build_context_path", type="Directory"),
        ],
        implementation=ContainerImplementation(
            container=ContainerSpec(
                image="alpine",
                command=[
                    "/bin/sh",
                    "-ex",
                    "-c",
                    'mkdir -p "$2"\n'
                    'echo "$1" > "$2/data.py"\n'
                    'cat << EOF > "$2/Dockerfile"\n'
                    f"FROM {analytics_client_base}\n"
                    "RUN python -m pip install --no-cache-dir $0\n"
                    "COPY data.py /app/flwr_analytics_client/data.py\n"
                    'ENTRYPOINT [ "python3", "/app/main.py" ]\n'
                    "EOF\n"
                    'ls "$2"',
                    InputValuePlaceholder("pip_packages"),
                    InputValuePlaceholder("python_script"),
                    OutputPathPlaceholder("build_context_path"),
                ],
            )
        ),
    )
    component = load_component(component_spec=prepare_context_spec)

    # pylint: disable-next=not-callable
    prepare_context_op: ContainerOp = component(" ".join(packages), data_func)
    prepare_context_op.enable_caching = False

    return prepare_context_op


@dataclass
class Parameter:
    """Parameter describes an input parameter of a Kubeflow pipeline component."""

    input_spec: InputSpec
    command_parameter: str
    command_placeholder: Union[InputValuePlaceholder, InputPathPlaceholder]


def analytics_server_spec(
    server_image: str,
    subcommand: str,
    parameters: Optional[Iterable[Parameter]] = None,
) -> ComponentSpec:
    """Component to run a Flower server for federated analytics."""
    if parameters is None:
        parameters = []

    inputs = [
        InputSpec("min_available_clients", type="Integer"),
    ]

    command = [
        "python3",
        "-m",
        "flwr_analytics_server",
        "--min-available-clients",
        InputValuePlaceholder("min_available_clients"),
        "--metadata-output-path",
        OutputPathPlaceholder("MLPipeline_ui_metadata"),
        subcommand,
    ]

    for parameter in parameters:
        inputs.append(parameter.input_spec)

        command.append(parameter.command_parameter)
        command.append(parameter.command_placeholder)

    spec = ComponentSpec(
        name="Flower Server",
        description="Start a Flower server for Federated Analytics",
        metadata=MetadataSpec(
            labels={
                "katulu/fl-server": "flower-server",
            },
        ),
        inputs=inputs,
        outputs=[
            OutputSpec("MLPipeline_ui_metadata", type="UI metadata"),
        ],
        implementation=ContainerImplementation(
            ContainerSpec(
                image=server_image,
                env={
                    "PYTHONPATH": "${PYTHONPATH}:/pipelines/component",
                },
                command=command,
            )
        ),
    )
    return spec
