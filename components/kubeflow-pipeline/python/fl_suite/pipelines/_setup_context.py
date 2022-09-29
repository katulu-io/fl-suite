import os

from kfp.components import load_component
from kfp.components.structures import (
    ComponentSpec,
    ContainerImplementation,
    ContainerSpec,
    OutputPathPlaceholder,
    OutputSpec,
)
from kfp.v2.dsl import ContainerOp

from fl_suite.context import Context


def setup_context(image_name: str, context: Context) -> ContainerOp:
    """Component to prepare a container build context for a small Python application."""
    copy_commands = ""
    subdir_list = []
    for path in context.file_paths:
        remote_path = os.path.relpath(path, context.base_dir)
        remote_dirname = os.path.dirname(remote_path)
        if remote_dirname not in subdir_list:
            subdir_list.append(remote_dirname)
            copy_commands += f'mkdir -p "$0/{remote_dirname}"\n'
        copy_commands += f"""cat <<EOF > "$0/{remote_path}"
{path.read_text()}
EOF
"""

    component_spec = ComponentSpec(
        name=f"setup-build-context-{image_name}",
        inputs=[],
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
                ],
                args=[
                    f'{copy_commands}\nls "$0"',
                    OutputPathPlaceholder("build_context_path"),
                ],
            )
        ),
    )
    component = load_component(component_spec=component_spec)

    # pylint: disable-next=not-callable
    container_op: ContainerOp = component()
    container_op.enable_caching = False

    return container_op
