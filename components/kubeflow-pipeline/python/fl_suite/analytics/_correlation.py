import inspect
import itertools
import textwrap
from functools import wraps
from typing import Callable, List, Optional

import numpy as np
from kfp.components import load_component
from kfp.components.structures import (
    ComponentSpec,
    ContainerImplementation,
    ContainerSpec,
    InputSpec,
    InputValuePlaceholder,
    OutputPathPlaceholder,
    OutputSpec,
)
from kfp.dsl import ContainerOp

from .._version import __version__
from ..pipelines import FLParameters, run


def data(
    packages: Optional[List[str]] = None,
) -> Callable[[Callable[[], np.ndarray]], ContainerOp]:
    """Decorator for an analytics data provider.

    The data provided by this function is used to calculate federated correlation.
    On the client, certain properties of this data is extracted and sent to the server."""
    if packages is None:
        packages = []

    def _wrapped(func: Callable[[], np.ndarray]) -> Callable[[], ContainerOp]:
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
        def _inner() -> ContainerOp:
            return prepare_correlation_client(func_code, packages)

        return _inner

    return _wrapped


def prepare_correlation_client(data_func: str, packages: List[str]) -> ContainerOp:
    """Instructions to build a client image for federated correlation."""
    aggregation_client_base = f"ghcr.io/katulu-io/fl-suite/correlation-client:{__version__}"

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
                    f"FROM {aggregation_client_base}\n"
                    "RUN python -m pip install --no-cache-dir $0\n"
                    "COPY data.py /pipelines/component/flwr_correlation_client/data.py\n"
                    'ENTRYPOINT [ "python3", "/pipelines/component/flwr_correlation_client" ]\n'
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


def correlate(
    data_func: Callable[[], ContainerOp],
    min_available_clients: int = 2,
    host: Optional[str] = None,
    experiment_name: Optional[str] = None,
) -> None:
    """Run distributed correlation of data provided by multiple clients."""
    aggregation_server = f"ghcr.io/katulu-io/fl-suite/correlation-server:{__version__}"

    run(
        fl_client=data_func,
        fl_server_image=aggregation_server,
        fl_params=FLParameters(
            num_rounds=1,
            min_available_clients=min_available_clients,
        ),
        host=host,
        experiment_name=experiment_name,
    )
