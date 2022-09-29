from typing import Optional

from kfp.components import load_component
from kfp.components._structures import (
    ComponentSpec,
    ContainerImplementation,
    ContainerSpec,
    InputPathPlaceholder,
    InputSpec,
    InputValuePlaceholder,
    OutputPathPlaceholder,
    OutputSpec,
)
from kfp.v2.dsl import ContainerOp
from kubernetes import client as k8s_client

from .._version import __version__

RESOURCE_ID = "{{workflow.name}}"


def save_ml_model(
    ml_model_path: str,
    minio_bucket: str,
    minio_path: str,
    minio_address: Optional[str] = "minio-service.kubeflow:9000",
    minio_protocol: Optional[str] = "http://",
) -> ContainerOp:
    """Component to save a ml model in minio."""
    # pylint: disable-next=fixme
    # TODO: Specify model version
    model_version = "0001"
    component_spec = ComponentSpec(
        name="Save ML model",
        inputs=[
            InputSpec(name="ml_model_path", type="Directory"),
            InputSpec(name="minio_bucket", type="String"),
            InputSpec(name="minio_path", type="Directory"),
            InputSpec(name="minio_address", type="String"),
            InputSpec(name="minio_protocol", type="String"),
        ],
        outputs=[
            OutputSpec(name="minio_full_path", type="Path"),
        ],
        implementation=ContainerImplementation(
            container=ContainerSpec(
                image="minio/mc:RELEASE.2022-05-09T04-08-26Z",
                command=[
                    "/bin/sh",
                    "-ex",
                    "-c",
                    "awk 'FNR==1{print}' /minio/{accesskey,secretkey} | "
                    'mc alias set minio "$1$2"\n'
                    "mc mb minio/$3 || true \n"
                    f'mc cp -r "$0"/ "minio/$3/$4/{model_version}"\n'
                    'mkdir -p "$(dirname "$5")"\n'
                    'echo "s3://$3/$4" > "$5"\n',
                    InputPathPlaceholder("ml_model_path"),
                    InputValuePlaceholder("minio_protocol"),
                    InputValuePlaceholder("minio_address"),
                    InputValuePlaceholder("minio_bucket"),
                    InputValuePlaceholder("minio_path"),
                    OutputPathPlaceholder("minio_full_path"),
                ],
            )
        ),
    )
    component = load_component(component_spec=component_spec)
    # pylint: disable-next=not-callable
    container_op: ContainerOp = component(
        ml_model_path,
        minio_bucket=minio_bucket,
        minio_path=minio_path,
        minio_address=minio_address,
        minio_protocol=minio_protocol,
    )
    container_op.enable_caching = False
    container_op.add_volume(
        k8s_client.V1Volume(
            name="minio-credentials",
            secret=k8s_client.V1SecretVolumeSource(secret_name="mlpipeline-minio-artifact"),
        ),
    )
    container_op.add_volume_mount(
        k8s_client.V1VolumeMount(name="minio-credentials", mount_path="/minio")
    )

    return container_op


def serve_ml_model(minio_ml_model_path: str) -> ContainerOp:
    """Component to create Kubernetes resources necessary for Federated Learning."""
    inference_service_yaml = f"""
---
apiVersion: serving.kubeflow.org/v1beta1
kind: InferenceService
metadata:
  name: {RESOURCE_ID}
spec:
  predictor:
    serviceAccountName: inference-service
    tensorflow:
      storageUri: "$(cat "$0")"
"""
    component_spec = ComponentSpec(
        name="Serve ML Model",
        inputs=[
            InputSpec(name="minio_ml_model_path", type="Path"),
        ],
        implementation=ContainerImplementation(
            ContainerSpec(
                image="gcr.io/cloud-builders/kubectl",
                command=["sh", "-ex", "-c"],
                args=[
                    f"kubectl -n katulu-fl apply -f - << EOF\n{inference_service_yaml}\nEOF",
                    InputPathPlaceholder("minio_ml_model_path"),
                ],
            )
        ),
    )
    component = load_component(component_spec=component_spec)
    # pylint: disable-next=not-callable
    container_op: ContainerOp = component(minio_ml_model_path=minio_ml_model_path)
    container_op.enable_caching = False

    return container_op
