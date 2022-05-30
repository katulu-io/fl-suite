from typing import List

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
from kfp.v2.dsl import ContainerOp
from kubernetes import client as k8s_client


def prepare_context(main: str, base_image: str, packages: List[str]) -> ContainerOp:
    """Component to prepare a container build context for a small Python application."""
    prepare_context_spec = ComponentSpec(
        name="Prepare build context",
        inputs=[
            InputSpec(name="base_image", type="String"),
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
                    'mkdir -p "$3"\n'
                    'echo "$2" > "$3/main.py"\n'
                    'cat << EOF > "$3/Dockerfile"\n'
                    "FROM $0\n"
                    "RUN python -m pip install --no-cache-dir $1\n"
                    "COPY main.py /app/\n"
                    'ENTRYPOINT [ "python", "/app/main.py" ]\n'
                    "EOF\n"
                    'ls "$3"',
                    InputValuePlaceholder("base_image"),
                    InputValuePlaceholder("pip_packages"),
                    InputValuePlaceholder("python_script"),
                    OutputPathPlaceholder("build_context_path"),
                ],
            )
        ),
    )
    component = load_component(component_spec=prepare_context_spec)

    # pylint: disable-next=not-callable
    prepare_context_op: ContainerOp = component(base_image, " ".join(packages), main)
    prepare_context_op.enable_caching = False

    return prepare_context_op


def download_build_context(
    minio_path: str, minio_url: str = "http://minio-service.kubeflow:9000"
) -> ContainerOp:
    """Component to expose a minio source as build context."""
    download_minio_files_spec = ComponentSpec(
        name="Prepare build context",
        inputs=[
            InputSpec(name="minio_url", type="String"),
            InputSpec(name="minio_path", type="String"),
        ],
        outputs=[
            OutputSpec(name="build_context_path", type="Directory"),
        ],
        implementation=ContainerImplementation(
            container=ContainerSpec(
                image="minio/mc:RELEASE.2022-05-09T04-08-26Z",
                command=[
                    "/bin/sh",
                    "-ex",
                    "-c",
                    'mkdir -p "$2"\n'
                    "awk 'FNR==1{print}' /minio/{accesskey,secretkey} | "
                    'mc alias set minio "$0"\n'
                    'mc cp -r "minio/$1/" "$2"\n',
                    InputValuePlaceholder("minio_url"),
                    InputValuePlaceholder("minio_path"),
                    OutputPathPlaceholder("build_context_path"),
                ],
            )
        ),
    )
    component = load_component(component_spec=download_minio_files_spec)

    # pylint: disable-next=not-callable
    download_minio_files_op: ContainerOp = component(minio_path=minio_path, minio_url=minio_url)
    download_minio_files_op.enable_caching = False
    download_minio_files_op.add_volume(
        k8s_client.V1Volume(
            name="minio-credentials",
            secret=k8s_client.V1SecretVolumeSource(secret_name="mlpipeline-minio-artifact"),
        ),
    )
    download_minio_files_op.add_volume_mount(
        k8s_client.V1VolumeMount(name="minio-credentials", mount_path="/minio")
    )

    return download_minio_files_op
