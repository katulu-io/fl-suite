from typing import Callable, Optional

from kfp import Client
from kfp.components import load_component
from kfp.dsl import ContainerOp, ExitHandler, pipeline

from .._version import __version__
from ..pipelines import (
    add_envoy_proxy,
    build_image,
    cleanup_kubernetes_resources,
    create_image_tag,
    setup_kubernetes_resources,
)
from ._analytics import analytics_server_spec


# pylint: disable-next=too-many-arguments
def correlate(
    data_func: Callable[[str, bool], ContainerOp],
    min_available_clients: int = 2,
    host: Optional[str] = None,
    experiment_name: Optional[str] = None,
    registry: str = "ghcr.io/katulu-io/fl-suite",
    verify_registry_tls: bool = True,
) -> None:
    """Run distributed correlation of data provided by multiple clients."""
    analytics_server = f"{registry}/analytics-server:{__version__}"

    client = Client(host)
    pipeline_run = client.create_run_from_pipeline_func(
        correlation_pipeline(
            fl_client=data_func,
            fl_server_image=analytics_server,
            registry=registry,
            verify_registry_tls=verify_registry_tls,
        ),
        arguments={
            "min_available_clients": min_available_clients,
        },
        experiment_name=experiment_name,
    )
    result = client.wait_for_run_completion(pipeline_run.run_id, timeout=3600)
    status = result.run.status.lower()

    if status in ["failed", "skipped", "error"]:
        raise RuntimeError(f"Run {status}")


def correlation_server(
    server_image: str,
    min_available_clients: int,
) -> ContainerOp:
    """Component to run a Flower server for federated correlation."""
    spec = analytics_server_spec(
        server_image=server_image,
        subcommand="correlation",
    )
    component = load_component(component_spec=spec)
    # pylint: disable-next=not-callable
    analytics_server_op: ContainerOp = component(
        min_available_clients,
    )
    analytics_server_op.enable_caching = False
    add_envoy_proxy(analytics_server_op)

    return analytics_server_op


def correlation_pipeline(
    registry: str,
    verify_registry_tls: bool,
    fl_client: Callable[[str, bool], ContainerOp],
    fl_server_image: str,
):
    """Creates a correlation pipeline."""

    @pipeline()
    def correlation(
        min_available_clients: int,
        image_tag: str = create_image_tag(),
    ) -> None:
        with ExitHandler(cleanup_kubernetes_resources()):
            prepare_context_op = fl_client(registry, verify_registry_tls)
            build_image(
                build_context_path=prepare_context_op.outputs["build_context_path"],
                image_name="flower-client",
                image_tag=image_tag,
                registry=registry,
                verify_registry_tls=verify_registry_tls,
            )

            setup_kubernetes_resources_op = setup_kubernetes_resources()
            analytics_server_op = correlation_server(
                fl_server_image,
                min_available_clients,
            )
            analytics_server_op.after(setup_kubernetes_resources_op)

    return correlation
