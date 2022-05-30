from datetime import datetime, timezone
from typing import Callable, Optional

from kfp import Client, dsl
from kfp.compiler import Compiler
from kfp.dsl import ContainerOp, ExitHandler
from kubernetes import client as k8s_client

from .._version import __version__
from ._build_image import build_image, static_image
from ._contants import REGISTRY_SECRET
from ._flower_infrastructure import cleanup_kubernetes_resources, setup_kubernetes_resources
from ._flower_server import FLParameters, flwr_server
from ._prepare_context import download_build_context


# pylint: disable-next=too-many-arguments
def _pipeline(
    registry: str,
    verify_registry_tls: bool,
    fl_client: Optional[Callable[[], ContainerOp]] = None,
    fl_client_context_url: Optional[str] = None,
    fl_client_image: Optional[str] = None,
    fl_server_image: Optional[str] = None,
):
    if fl_client is None and fl_client_context_url is None and fl_client_image is None:
        raise RuntimeError(
            "either of: 'fl_client', 'fl_client_context_url' or 'fl_client_image' has to be set"
        )

    if fl_server_image is None:
        fl_server_image = f"{registry}/fl-server:{__version__}"

    # pylint: disable=too-many-arguments
    @dsl.pipeline()
    def fl_pipeline(
        image_tag: str,
        num_rounds: int,
        num_local_rounds: int,
        min_available_clients: int,
        min_fit_clients: int,
        min_eval_clients: int,
    ) -> None:
        dsl.get_pipeline_conf().set_image_pull_secrets(
            [k8s_client.V1ObjectReference(name=REGISTRY_SECRET)]
        )

        with ExitHandler(cleanup_kubernetes_resources()):
            if fl_client is not None:
                prepare_context_op = fl_client()
                build_image(
                    build_context_path=prepare_context_op.outputs["build_context_path"],
                    image_tag=image_tag,
                    registry=registry,
                    verify_registry_tls=verify_registry_tls,
                )
            if fl_client_context_url is not None:
                download_build_context_op = download_build_context(fl_client_context_url)
                build_image(
                    build_context_path=download_build_context_op.outputs["build_context_path"],
                    image_tag=image_tag,
                    registry=registry,
                    verify_registry_tls=verify_registry_tls,
                )
            elif fl_client_image is not None:
                static_image(fl_client_image)

            setup_kubernetes_resources_op = setup_kubernetes_resources()
            flwr_server_op = flwr_server(
                fl_server_image,
                FLParameters(
                    num_rounds,
                    num_local_rounds,
                    min_available_clients,
                    min_fit_clients,
                    min_eval_clients,
                ),
            )
            flwr_server_op.after(setup_kubernetes_resources_op)

    return fl_pipeline


# pylint: disable-next=too-many-arguments
def build(
    fl_client: Optional[Callable[[], ContainerOp]] = None,
    fl_client_context_url: Optional[str] = None,
    fl_client_image: Optional[str] = None,
    fl_server_image: Optional[str] = None,
    package_path: str = ".",
    registry: str = "ghcr.io/katulu-io/fl-suite",
    verify_registry_tls=True,
) -> None:
    """Build a Kubeflow pipeline for federated learning."""

    fl_pipeline = _pipeline(
        fl_client=fl_client,
        fl_client_context_url=fl_client_context_url,
        fl_client_image=fl_client_image,
        fl_server_image=fl_server_image,
        registry=registry,
        verify_registry_tls=verify_registry_tls,
    )
    compiler = Compiler()
    compiler.compile(fl_pipeline, package_path)


# pylint: disable-next=too-many-arguments
def run(
    fl_client: Optional[Callable[[], ContainerOp]] = None,
    fl_client_context_url: Optional[str] = None,
    fl_client_image: Optional[str] = None,
    fl_server_image: Optional[str] = None,
    fl_params: Optional[FLParameters] = None,
    host: Optional[str] = None,
    image_tag: str = "",
    experiment_name: Optional[str] = None,
    registry: str = "ghcr.io/katulu-io/fl-suite",
    verify_registry_tls: bool = True,
):
    """Creates and runs a Kubeflow pipeline for federated learning.

    Args:
      client_context: (kubeflow's) minio path where the client code is hosted
      num_rounds: The number of rounds of training.
      num_local_rounds: The number of local training rounds.
      min_available_clients: Minimum number of clients to start training.
      min_fit_clients: Minimum number of clients used to fit weights.
      min_eval_clients: Minimum number of client used during evaluation.
      host: The host name to use to talk to Kubeflow Pipelines. If not set, the in-cluster
          service DNS name will be used, which only works if the current environment is a pod
          in the same cluster (such as a Jupyter instance spawned by Kubeflow's
          JupyterHub). If you have a different connection to cluster, such as a kubectl
          proxy connection, then set it to something like "127.0.0.1:8080/pipeline.
      image_tag: The client image name and tag to set.
      experiment_name: The Kubeflow Pipelines experiment to use.
      registry: Registry where to pull the docker images
      verify_registry_tls: Flag to verify or not the TLS connection to the registry
    """
    if fl_params is None:
        fl_params = FLParameters()

    if not image_tag:
        image_tag = _create_image_tag("fl-client")

    client = Client(host)
    pipeline_run = client.create_run_from_pipeline_func(
        _pipeline(
            fl_client=fl_client,
            fl_client_context_url=fl_client_context_url,
            fl_client_image=fl_client_image,
            fl_server_image=fl_server_image,
            registry=registry,
            verify_registry_tls=verify_registry_tls,
        ),
        arguments={
            "image_tag": image_tag,
            "num_rounds": fl_params.num_rounds,
            "num_local_rounds": fl_params.num_local_rounds,
            "min_available_clients": fl_params.min_available_clients,
            "min_fit_clients": fl_params.min_fit_clients,
            "min_eval_clients": fl_params.min_eval_clients,
        },
        experiment_name=experiment_name,
    )
    result = client.wait_for_run_completion(pipeline_run.run_id, timeout=3600)
    status = result.run.status.lower()

    if status in ["failed", "skipped", "error"]:
        raise RuntimeError(f"Run {status}")


def _create_image_tag(name: str) -> str:
    now = datetime.now(timezone.utc)
    tag = f"{now.year}.{now.month}.{now.day}-{now.hour}.{now.minute}"

    return f"{name}:{tag}"
