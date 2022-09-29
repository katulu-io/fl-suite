from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
from kfp.compiler import Compiler

from fl_suite.analytics import _correlation, data
from fl_suite.pipelines import training_pipeline
from fl_suite.context import context_from_func, context_from_python_files


@dataclass
class Task:
    """Test representation of a pipeline task"""

    name: str
    dependencies: Optional[List[str]] = None
    parameters: Optional[Dict[str, str]] = None
    artifacts: Optional[Dict[str, str]] = None


def test_fl_client_training():
    """Tests the fl pipeline using the fl_client decorator"""

    @context_from_func()
    def client():
        pass

    pipeline = parse_pipeline(
        training_pipeline(
            fl_client=client,
            registry="localhost:5000",
            verify_registry_tls=False,
        )
    )

    assert_exit_handler_in_pipeline(Task("cleanup-flower-server-infrastructure"), pipeline)

    assert_task_in_pipeline(Task("setup-build-context-flower-client"), pipeline)
    assert_task_in_pipeline(
        Task(
            "build-image-flower-client",
            dependencies=["setup-build-context-flower-client"],
            parameters={
                "image_tag": "{{inputs.parameters.image_tag}}",
            },
            artifacts={
                # pylint: disable-next=line-too-long
                "setup-build-context-flower-client-build_context_path": "{{tasks.setup-build-context-flower-client.outputs.artifacts.setup-build-context-flower-client-build_context_path}}"  # noqa
            },
        ),
        pipeline,
    )

    assert_task_in_pipeline(Task("setup-flower-server-infrastructure"), pipeline)
    assert_task_in_pipeline(
        Task(
            "flower-server",
            parameters={
                "min_available_clients": "{{inputs.parameters.min_available_clients}}",
                "min_eval_clients": "{{inputs.parameters.min_eval_clients}}",
                "min_fit_clients": "{{inputs.parameters.min_fit_clients}}",
                "num_local_rounds": "{{inputs.parameters.num_local_rounds}}",
                "num_rounds": "{{inputs.parameters.num_rounds}}",
            },
            dependencies=["setup-flower-server-infrastructure"],
        ),
        pipeline,
    )


def test_fl_client_context_from_files_training(dir_with_requirements: Path):
    """Tests the training pipeline using the client context url"""
    pipeline = parse_pipeline(
        training_pipeline(
            fl_client=context_from_python_files(
                src_dir=str(dir_with_requirements),
                entrypoint=["python3", "main.py"],
                python_packages=["torch", "flwr"],
            ),
            registry="localhost:5000",
            verify_registry_tls=False,
        )
    )

    assert_exit_handler_in_pipeline(Task("cleanup-flower-server-infrastructure"), pipeline)

    assert_task_in_pipeline(Task("setup-build-context-flower-client"), pipeline)
    assert_task_in_pipeline(
        Task(
            "build-image-flower-client",
            dependencies=["setup-build-context-flower-client"],
            parameters={"image_tag": "{{inputs.parameters.image_tag}}"},
            artifacts={
                # pylint: disable-next=line-too-long
                "setup-build-context-flower-client-build_context_path": "{{tasks.setup-build-context-flower-client.outputs.artifacts.setup-build-context-flower-client-build_context_path}}"  # noqa
            },
        ),
        pipeline,
    )
    assert_task_in_pipeline(
        Task(
            "flower-server",
            parameters={
                "min_available_clients": "{{inputs.parameters.min_available_clients}}",
                "min_eval_clients": "{{inputs.parameters.min_eval_clients}}",
                "min_fit_clients": "{{inputs.parameters.min_fit_clients}}",
                "num_local_rounds": "{{inputs.parameters.num_local_rounds}}",
                "num_rounds": "{{inputs.parameters.num_rounds}}",
            },
            dependencies=["setup-flower-server-infrastructure"],
        ),
        pipeline,
    )
    assert_task_in_pipeline(Task("setup-flower-server-infrastructure"), pipeline)


def test_static_client_and_custom_server_training():
    """Tests the training pipeline using a static client image and custom server"""

    @context_from_func()
    def server():
        pass

    pipeline = parse_pipeline(
        training_pipeline(
            fl_client="fl_client_image:latest",
            fl_server=server,
            registry="localhost:5000",
            verify_registry_tls=False,
        )
    )

    assert_exit_handler_in_pipeline(Task("cleanup-flower-server-infrastructure"), pipeline)

    assert_task_in_pipeline(Task("output-image-flower-client"), pipeline)

    assert_task_in_pipeline(Task("setup-flower-server-infrastructure"), pipeline)
    assert_task_in_pipeline(Task("setup-build-context-flower-server"), pipeline)
    assert_task_in_pipeline(
        Task(
            "build-image-flower-server",
            dependencies=["setup-build-context-flower-server"],
            parameters={
                "image_tag": "{{inputs.parameters.image_tag}}",
            },
            artifacts={
                # pylint: disable-next=line-too-long
                "setup-build-context-flower-server-build_context_path": "{{tasks.setup-build-context-flower-server.outputs.artifacts.setup-build-context-flower-server-build_context_path}}"  # noqa
            },
        ),
        pipeline,
    )
    assert_task_in_pipeline(
        Task(
            "flower-server",
            parameters={
                # pylint: disable-next=line-too-long
                "build-image-flower-server-image_url": "{{tasks.build-image-flower-server.outputs.parameters.build-image-flower-server-image_url}}",
                "min_available_clients": "{{inputs.parameters.min_available_clients}}",
                "min_eval_clients": "{{inputs.parameters.min_eval_clients}}",
                "min_fit_clients": "{{inputs.parameters.min_fit_clients}}",
                "num_local_rounds": "{{inputs.parameters.num_local_rounds}}",
                "num_rounds": "{{inputs.parameters.num_rounds}}",
            },
            dependencies=["build-image-flower-server", "setup-flower-server-infrastructure"],
        ),
        pipeline,
    )


def test_correlation_pipeline():
    """Test the correlation pipeline"""

    @data(packages=["numpy"])
    def client() -> np.ndarray:
        return np.zeros(1)

    # For ease of testing, we test directly against the fl correlation_pipeline.
    # pylint: disable-next=protected-access
    pipeline = parse_pipeline(
        _correlation.correlation_pipeline(
            fl_client=client,
            fl_server_image="ghcr.io/katulu-io/fl-suite/analytics-server:{__version__}",
            registry="localhost:5000",
            verify_registry_tls=False,
        )
    )

    assert_exit_handler_in_pipeline(Task("cleanup-flower-server-infrastructure"), pipeline)

    assert_task_in_pipeline(Task("prepare-build-context"), pipeline)
    assert_task_in_pipeline(
        Task(
            "build-image-flower-client",
            dependencies=["prepare-build-context"],
            parameters={"image_tag": "{{inputs.parameters.image_tag}}"},
            artifacts={
                # pylint: disable-next=line-too-long
                "prepare-build-context-build_context_path": "{{tasks.prepare-build-context.outputs.artifacts.prepare-build-context-build_context_path}}"  # noqa
            },
        ),
        pipeline,
    )
    assert_task_in_pipeline(
        Task(
            "flower-server",
            parameters={"min_available_clients": "{{inputs.parameters.min_available_clients}}"},
            dependencies=["setup-flower-server-infrastructure"],
        ),
        pipeline,
    )
    assert_task_in_pipeline(Task("setup-flower-server-infrastructure"), pipeline)


def parse_pipeline(pipeline) -> Dict[str, Any]:
    """Converts a pipeline to an argo workflow: dictionary representation"""

    compiler = Compiler()

    # _create_workflow is used to retrieve a parsed (dictionary) representation of the pipeline
    # pylint: disable-next=protected-access
    return compiler._create_workflow(pipeline)


def assert_exit_handler_in_pipeline(exit_handler: Task, parsed_pipeline: Dict[str, Any]):
    """Asserts that the given argo workflow has an exit handler"""

    assert exit_handler.name == parsed_pipeline["spec"]["onExit"]


def assert_task_in_pipeline(
    expected_task: Task,
    pipeline: Dict[Any, Any],
):
    """Asserts that a given task exists in the pipeline"""

    # Find and extracts the directed acylic graph from the parsed_pipeline
    entrypoint = find_by_name(pipeline["spec"]["templates"], pipeline["spec"]["entrypoint"])
    assert entrypoint is not None, "Entrypoint not found"
    main_task = find_by_name(pipeline["spec"]["templates"], entrypoint["dag"]["tasks"][0]["name"])
    assert main_task is not None, "Main task not found"
    dag = main_task["dag"]

    # Find and check that the task exists inside the dag
    dag_task = find_by_name(dag["tasks"], expected_task.name)
    assert dag_task is not None, f'"{expected_task.name}" task not found'

    if expected_task.dependencies is not None:
        assert (
            dag_task["dependencies"] == expected_task.dependencies
        ), f'"{expected_task.name}" task do not have the expected dependencies'

    if expected_task.parameters is not None:
        expected_parameters = [
            {"name": name, "value": value} for name, value in expected_task.parameters.items()
        ]
        assert (
            dag_task["arguments"].get("parameters") == expected_parameters
        ), f'"{expected_task.name}" task do not have the expected parameters'

    if expected_task.artifacts is not None:
        expected_artifacts = [
            {"name": name, "from": value} for name, value in expected_task.artifacts.items()
        ]
        assert (
            dag_task["arguments"].get("artifacts") == expected_artifacts
        ), f'"{expected_task.name}" task do not have the expected artifacts'


def find_by_name(template_list, template_name: str) -> Optional[Dict[Any, Any]]:
    """Finds a dictionary by the "name" key"""

    for template in template_list:
        if template["name"] == template_name:
            return template

    return None
