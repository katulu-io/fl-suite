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
from kfp.v2.dsl import ContainerOp
from kubernetes import client as k8s_client

from .._version import __version__
from ._contants import INTERNAL_REGISTRY_SECRET


def build_image(
    build_context_path: str,
    image_name: str,
    image_tag: str,
    registry: str = "ghcr.io/katulu-io/fl-suite",
    verify_registry_tls: bool = True,
) -> ContainerOp:
    """Component to build a multi-arch container from a build context."""
    build_image_spec = ComponentSpec(
        name=f"build-image-{image_name}",
        metadata=MetadataSpec(
            labels={"katulu/fl-client": image_name},
        ),
        inputs=[
            InputSpec(name="build_context_path", type="Directory"),
            InputSpec(name="image_name", type="String"),
            InputSpec(name="image_tag", type="String"),
            InputSpec(name="verify_registry_tls", type="Boolean"),
        ],
        outputs=[
            OutputSpec(name="image_url", type="String"),
        ],
        implementation=ContainerImplementation(
            ContainerSpec(
                image=f"{registry}/image-builder:{__version__}",
                command=[
                    "/build.sh",
                    InputPathPlaceholder("build_context_path"),
                    InputValuePlaceholder("image_name"),
                    InputValuePlaceholder("image_tag"),
                    OutputPathPlaceholder("image_url"),
                    InputValuePlaceholder("verify_registry_tls"),
                ],
            )
        ),
    )
    component = load_component(component_spec=build_image_spec)
    # pylint: disable-next=not-callable
    build_image_op: ContainerOp = component(
        build_context_path, image_name, image_tag, verify_registry_tls
    )
    build_image_op.enable_caching = False
    build_image_op.add_volume(
        k8s_client.V1Volume(
            name="docker-config",
            secret=k8s_client.V1SecretVolumeSource(
                secret_name=INTERNAL_REGISTRY_SECRET,
                items=[k8s_client.V1KeyToPath(key=".dockerconfigjson", path="config.json")],
            ),
        ),
    )
    build_image_op.add_volume_mount(
        k8s_client.V1VolumeMount(name="docker-config", mount_path="/.docker")
    )
    build_image_op.container.add_resource_limit("smarter-devices/fuse", "1")
    build_image_op.container.add_resource_request("smarter-devices/fuse", "1")

    return build_image_op


def output_image(
    image_name: str, image_tag: str, registry: str = "ghcr.io/katulu-io/fl-suite"
) -> ContainerOp:
    """Component to reference a container image"""
    component_spec = ComponentSpec(
        name=f"output-image-{image_name}",
        metadata=MetadataSpec(
            labels={"katulu/fl-client": image_name},
        ),
        inputs=[
            InputSpec(name="image_name", type="String"),
            InputSpec(name="image_tag", type="String"),
        ],
        outputs=[
            OutputSpec(name="image_url", type="Path"),
        ],
        implementation=ContainerImplementation(
            ContainerSpec(
                image=f"{registry}/image-builder:{__version__}",
                command=[
                    "sh",
                    "-ex",
                    "-c",
                    "REGISTRY=$(jq -r '.auths | keys[0]' /.docker/config.json "
                    "| sed -e 's/https:\\/\\///')\n"
                    'mkdir -p "$(dirname "$2")"\n'
                    'echo "$REGISTRY/$0:$1" > "$2"\n',
                    InputValuePlaceholder("image_name"),
                    InputValuePlaceholder("image_tag"),
                    OutputPathPlaceholder("image_url"),
                ],
            )
        ),
    )
    component = load_component(component_spec=component_spec)
    # pylint: disable-next=not-callable
    container_op: ContainerOp = component(image_name, image_tag)
    container_op.add_volume(
        k8s_client.V1Volume(
            name="docker-config",
            secret=k8s_client.V1SecretVolumeSource(
                secret_name=INTERNAL_REGISTRY_SECRET,
                items=[k8s_client.V1KeyToPath(key=".dockerconfigjson", path="config.json")],
            ),
        ),
    )
    container_op.add_volume_mount(
        k8s_client.V1VolumeMount(name="docker-config", mount_path="/.docker")
    )

    return container_op
