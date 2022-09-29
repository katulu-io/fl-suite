from datetime import datetime, timezone
from typing import Callable, List, Optional, Tuple, Union

from kfp import Client, dsl
from kfp.compiler import Compiler
from kfp.dsl import ExitHandler
from kubernetes import client as k8s_client

from fl_suite.context import Context

from .._version import __version__
from ._build_image import build_image, output_image
from ._contants import INTERNAL_REGISTRY_SECRET
from ._flower_infrastructure import cleanup_kubernetes_resources, setup_kubernetes_resources
from ._flower_server import FLOutput, FLParameters, flwr_server
from ._ml_model import save_ml_model, serve_ml_model
from ._setup_context import setup_context

ContainerImageSpec = Union[Callable[[], Context], Context, str]

# pylint: disable-next=too-many-arguments
def training_pipeline(
    fl_client: ContainerImageSpec,
    fl_server: Optional[ContainerImageSpec] = None,
    fl_outputs: Optional[List[FLOutput]] = None,
    registry: str = "ghcr.io/katulu-io/fl-suite",
    verify_registry_tls: bool = True,
):
    """Federated learning training pipeline.

    Args:
      fl_client: Container image specification for the federated learning client:
        - str: image_tag of the flower-client built in the fl-suite.
        - Callable[[], Context]: "context_from_func" decorated function. Used to define context's
          from python functions.
        - Context: "context_from_func" decorated function
      fl_server: Container image specification for the federated learning server. Same as fl_client.
      registry: Registry where to pull the docker images
      verify_registry_tls: Flag to verify or not the TLS connection to the registry
    """

    if fl_server is None:
        fl_server = f"{registry}/fl-server:{__version__}"

    # pylint: disable-next=fixme
    # TODO: To define a complete custom flower-server we need to be able to pass pipeline arguments
    # dynamically. Unfortunately this cannot be achieved with the standard way: **kwargs otherwise
    # this errors is raised: "takes from 0 to 1 positional arguments but 2 were given"
    @dsl.pipeline()
    def fl_pipeline(
        image_tag: str = create_image_tag(),
        num_rounds: int = 3,
        num_local_rounds: int = 1,
        min_available_clients: int = 2,
        min_fit_clients: int = 2,
        min_eval_clients: int = 2,
    ) -> None:
        with ExitHandler(cleanup_kubernetes_resources()):
            if isinstance(fl_client, str):
                output_image(
                    image_name="flower-client",
                    image_tag=fl_client,
                    registry=registry,
                )
            else:
                _build_container_image(
                    fl_client,
                    image_name="flower-client",
                    image_tag=image_tag,
                    registry=registry,
                    verify_registry_tls=verify_registry_tls,
                )

            setup_kubernetes_resources_op = setup_kubernetes_resources()
            fl_server_image_url = ""
            entrypoint = []
            if isinstance(fl_server, str):
                fl_server_image_url = fl_server
                # We assume the flower-server entrypoint is the one defined in:
                # components/kubeflow-pipeline/pipeline_components/flwr-server/Dockerfile
                entrypoint = ["python3", "flwr_server"]
            else:
                fl_server_image_url, entrypoint = _build_container_image(
                    fl_server,
                    image_name="flower-server",
                    image_tag=image_tag,
                    registry=registry,
                    verify_registry_tls=verify_registry_tls,
                )

            flwr_server_op = flwr_server(
                container_image=fl_server_image_url,
                entrypoint=entrypoint,
                fl_outputs=fl_outputs,
                fl_params=FLParameters(
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
def training_and_serving_pipeline(
    fl_client: ContainerImageSpec,
    fl_server: Optional[ContainerImageSpec] = None,
    fl_outputs: Optional[List[FLOutput]] = None,
    registry: str = "ghcr.io/katulu-io/fl-suite",
    verify_registry_tls: bool = True,
):
    """Federated learning training and serving pipeline.

    Args:
      fl_client: Container image specification for the federated learning client:
        - str: image_tag of the flower-client built in the fl-suite.
        - Callable[[], Context]: "context_from_func" decorated function. Used to define context's
          from python functions.
        - Context: "context_from_func" decorated function
      fl_server: Container image specification for the federated learning server. Same as fl_client.
      registry: Registry where to pull the docker images
      verify_registry_tls: Flag to verify or not the TLS connection to the registry
    """

    if fl_server is None:
        fl_server = f"{registry}/fl-server:{__version__}"

    # pylint: disable-next=fixme
    # TODO: To define a complete custom flower-server we need to be able to pass pipeline arguments
    # dynamically. Unfortunately this cannot be achieved with the standard way: **kwargs otherwise
    # this errors is raised: "takes from 0 to 1 positional arguments but 2 were given"
    @dsl.pipeline()
    def fl_pipeline(
        image_tag: str = create_image_tag(),
        num_rounds: int = 3,
        num_local_rounds: int = 1,
        min_available_clients: int = 2,
        min_fit_clients: int = 2,
        min_eval_clients: int = 2,
    ) -> None:
        with ExitHandler(cleanup_kubernetes_resources()):
            if isinstance(fl_client, str):
                output_image(
                    image_name="flower-client",
                    image_tag=fl_client,
                    registry=registry,
                )
            else:
                _build_container_image(
                    fl_client,
                    image_name="flower-client",
                    image_tag=image_tag,
                    registry=registry,
                    verify_registry_tls=verify_registry_tls,
                )

            setup_kubernetes_resources_op = setup_kubernetes_resources()
            fl_server_image_url = ""
            entrypoint = []
            if isinstance(fl_server, str):
                fl_server_image_url = fl_server
                # We assume the flower-server entrypoint is the one defined in:
                # components/kubeflow-pipeline/pipeline_components/flwr-server/Dockerfile
                entrypoint = ["python3", "flwr_server"]
            else:
                fl_server_image_url, entrypoint = _build_container_image(
                    fl_server,
                    image_name="flower-server",
                    image_tag=image_tag,
                    registry=registry,
                    verify_registry_tls=verify_registry_tls,
                )

            flwr_server_op = flwr_server(
                container_image=fl_server_image_url,
                entrypoint=entrypoint,
                fl_outputs=fl_outputs,
                fl_params=FLParameters(
                    num_rounds,
                    num_local_rounds,
                    min_available_clients,
                    min_fit_clients,
                    min_eval_clients,
                ),
            )
            flwr_server_op.after(setup_kubernetes_resources_op)
            save_ml_model_op = save_ml_model(
                flwr_server_op.outputs["ml_model_path"],
                "ml-model",
                "{{workflow.name}}",
            )
            serve_ml_model(save_ml_model_op.outputs["minio_full_path"])

    return fl_pipeline


def _build_container_image(
    container_image_spec: Union[Callable[[], Context], Context],
    image_name: str,
    image_tag: str,
    registry: str,
    verify_registry_tls: bool,
) -> Tuple[str, List[str]]:
    container_context: Context
    if callable(container_image_spec):
        container_context = container_image_spec()
    elif isinstance(container_image_spec, Context):
        container_context = container_image_spec

    setup_context_op = setup_context(image_name, container_context)

    build_image_op = build_image(
        build_context_path=setup_context_op.outputs["build_context_path"],
        image_name=image_name,
        image_tag=image_tag,
        registry=registry,
        verify_registry_tls=verify_registry_tls,
    )

    return (build_image_op.outputs["image_url"], container_context.entrypoint)


# pylint: disable-next=too-many-arguments
def build(
    pipeline: Callable[..., None],
    package_path: str = "pipeline.yaml",
) -> None:
    """Build a FL-Suite pipeline."""

    compiler = Compiler()
    pipeline_conf = dsl.PipelineConf()
    pipeline_conf.set_image_pull_secrets(
        [
            k8s_client.V1ObjectReference(
                name=INTERNAL_REGISTRY_SECRET,
            )
        ],
    )
    compiler.compile(pipeline, package_path, pipeline_conf=pipeline_conf)


# pylint: disable-next=too-many-arguments
def run(
    pipeline: Callable[..., None],
    fl_params: Optional[FLParameters] = None,
    host: Optional[str] = None,
    image_tag: str = "",
    experiment_name: Optional[str] = None,
):
    """Creates and runs a FL-Suite pipeline.

    Args:
      pipeline: Pipeline (function) to run
      fl_params: Parameters for the federated learning training
      host: The host name to use to talk to Kubeflow Pipelines. If not set, the in-cluster
          service DNS name will be used, which only works if the current environment is a pod
          in the same cluster (such as a Jupyter instance spawned by Kubeflow's
          JupyterHub). If you have a different connection to cluster, such as a kubectl
          proxy connection, then set it to something like "127.0.0.1:8080/pipeline.
      image_tag: The tag to set.
      experiment_name: The Kubeflow Pipelines experiment to use.
    """
    if fl_params is None:
        fl_params = FLParameters()

    if not image_tag:
        image_tag = create_image_tag()

    client = Client(host)
    pipeline_conf = dsl.PipelineConf()
    pipeline_conf.set_image_pull_secrets(
        [
            k8s_client.V1ObjectReference(
                name=INTERNAL_REGISTRY_SECRET,
            )
        ],
    )
    pipeline_run = client.create_run_from_pipeline_func(
        pipeline,
        arguments={
            "image_tag": image_tag,
            "num_rounds": fl_params.num_rounds,
            "num_local_rounds": fl_params.num_local_rounds,
            "min_available_clients": fl_params.min_available_clients,
            "min_fit_clients": fl_params.min_fit_clients,
            "min_eval_clients": fl_params.min_eval_clients,
        },
        experiment_name=experiment_name,
        pipeline_conf=pipeline_conf,
    )
    result = client.wait_for_run_completion(pipeline_run.run_id, timeout=3600)
    status = result.run.status.lower()

    if status in ["failed", "skipped", "error"]:
        raise RuntimeError(f"Run {status}")


def create_image_tag() -> str:
    """Create an image tag."""
    now = datetime.now(timezone.utc)

    return f"{now.year}.{now.month}.{now.day}-{now.hour}.{now.minute}"
