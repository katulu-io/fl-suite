from typing import Callable, Optional, Tuple

from kfp import Client
from kfp.components import load_component
from kfp.components._structures import InputSpec, InputValuePlaceholder
from kfp.dsl import ContainerOp, ExitHandler, pipeline

from .._version import __version__
from ..pipelines import (
    add_envoy_proxy,
    build_image,
    cleanup_kubernetes_resources,
    create_image_tag,
    setup_kubernetes_resources,
)
from ._analytics import Parameter, analytics_server_spec


# pylint: disable-next=too-many-arguments
def boxplot(
    data_func: Callable[[str, bool], ContainerOp],
    nbins: int,
    hrange: Tuple[float, float],
    min_available_clients: int = 2,
    host: Optional[str] = None,
    experiment_name: Optional[str] = None,
    registry: str = "ghcr.io/katulu-io/fl-suite",
    verify_registry_tls: bool = True,
) -> None:
    """Run distributed boxplot of data provided by multiple clients."""
    analytics_server = f"{registry}/analytics-server:{__version__}"

    client = Client(host)
    pipeline_run = client.create_run_from_pipeline_func(
        boxplot_pipeline(
            fl_client=data_func,
            fl_server_image=analytics_server,
            registry=registry,
            verify_registry_tls=verify_registry_tls,
        ),
        arguments={
            "min_available_clients": min_available_clients,
            "nbins": nbins,
            "hmin": hrange[0],
            "hmax": hrange[1],
        },
        experiment_name=experiment_name,
    )
    result = client.wait_for_run_completion(pipeline_run.run_id, timeout=3600)
    status = result.run.status.lower()

    if status in ["failed", "skipped", "error"]:
        raise RuntimeError(f"Run {status}")


def boxplot_server(
    server_image: str,
    min_available_clients: int,
    nbins: int,
    hrange: Tuple[float, float],
) -> ContainerOp:
    """Component to run a Flower server for federated boxplot."""
    spec = analytics_server_spec(
        server_image=server_image,
        subcommand="boxplot",
        parameters=[
            Parameter(
                InputSpec("nbins", type="Integer"),
                "--nbins",
                InputValuePlaceholder("nbins"),
            ),
            Parameter(
                InputSpec("hmin", type="Float"),
                "--hmin",
                InputValuePlaceholder("hmin"),
            ),
            Parameter(
                InputSpec("hmax", type="Float"),
                "--hmax",
                InputValuePlaceholder("hmax"),
            ),
        ],
    )
    component = load_component(component_spec=spec)
    # pylint: disable-next=not-callable
    analytics_server_op: ContainerOp = component(
        min_available_clients,
        nbins,
        hrange[0],
        hrange[1],
    )
    analytics_server_op.enable_caching = False
    add_envoy_proxy(analytics_server_op)

    return analytics_server_op


def boxplot_pipeline(
    registry: str,
    verify_registry_tls: bool,
    fl_client: Callable[[str, bool], ContainerOp],
    fl_server_image: str,
):
    """Create a boxplot pipeline."""

    # pylint: disable-next=too-many-arguments
    @pipeline(name="boxplot")
    def h_pipeline(
        min_available_clients: int,
        nbins: int,
        hmin: float,
        hmax: float,
        image_tag: str = create_image_tag(),
    ) -> None:
        with ExitHandler(cleanup_kubernetes_resources()):
            prepare_context_op = fl_client(registry, verify_registry_tls)
            build_image(
                build_context_path=prepare_context_op.outputs["build_context_path"],
                image_name="boxplot-client",
                image_tag=image_tag,
                registry=registry,
                verify_registry_tls=verify_registry_tls,
            )

            setup_kubernetes_resources_op = setup_kubernetes_resources()
            analytics_server_op = boxplot_server(
                fl_server_image, min_available_clients, nbins, (hmin, hmax)
            )
            analytics_server_op.after(setup_kubernetes_resources_op)

    return h_pipeline
