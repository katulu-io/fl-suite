from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
from kfp.compiler import Compiler

from fl_suite.analytics import _correlation, data
from fl_suite.pipelines import training_pipeline, fl_client


@dataclass
class Task:
    """Test representation of a pipeline task"""

    name: str
    dependencies: Optional[List[str]] = None
    parameters: Optional[Dict[str, str]] = None
    artifacts: Optional[Dict[str, str]] = None


def test_fl_client_training():
    """Tests the fl pipeline using the fl_client decorator"""

    @fl_client()
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

    assert_task_in_pipeline(Task("prepare-build-context"), pipeline)
    assert_task_in_pipeline(
        Task(
            "fl-client-image-builder",
            dependencies=["prepare-build-context"],
            parameters={"image_tag": "{{inputs.parameters.image_tag}}"},
            artifacts={
                # pylint: disable-next=line-too-long
                "prepare-build-context-build_context_path": "{{tasks.prepare-build-context.outputs.artifacts.prepare-build-context-build_context_path}}"  # noqa
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


def test_fl_client_context_url_training():
    """Tests the training pipeline using the client context url"""

    pipeline = parse_pipeline(
        training_pipeline(
            fl_client_context_url="a-non-existing-context-url",
            registry="localhost:5000",
            verify_registry_tls=False,
        )
    )

    assert_exit_handler_in_pipeline(Task("cleanup-flower-server-infrastructure"), pipeline)

    assert_task_in_pipeline(Task("prepare-build-context"), pipeline)
    assert_task_in_pipeline(
        Task(
            "fl-client-image-builder",
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


def test_fl_client_image_training():
    """Tests the training pipeline using a static client image"""

    pipeline = parse_pipeline(
        training_pipeline(
            fl_client_image="fl_client_image:latest",
            registry="localhost:5000",
            verify_registry_tls=False,
        )
    )

    assert_exit_handler_in_pipeline(Task("cleanup-flower-server-infrastructure"), pipeline)

    assert_task_in_pipeline(Task("fl-client-image"), pipeline)
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
            "fl-client-image-builder",
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
        assert dag_task["dependencies"] == expected_task.dependencies

    if expected_task.parameters is not None:
        expected_parameters = [
            {"name": name, "value": value} for name, value in expected_task.parameters.items()
        ]
        assert dag_task["arguments"]["parameters"] == expected_parameters

    if expected_task.artifacts is not None:
        expected_artifacts = [
            {"name": name, "from": value} for name, value in expected_task.artifacts.items()
        ]
        assert dag_task["arguments"]["artifacts"] == expected_artifacts


def find_by_name(template_list, template_name: str) -> Optional[Dict[Any, Any]]:
    """Finds a dictionary by the "name" key"""

    for template in template_list:
        if template["name"] == template_name:
            return template

    return None
