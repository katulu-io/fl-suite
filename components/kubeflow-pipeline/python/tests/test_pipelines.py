from typing import Any, Dict, List, Optional

import numpy as np
from kfp.compiler import Compiler

from fl_suite.analytics import _correlation, data
from fl_suite.pipelines import _pipelines, fl_client


def test_fl_pipeline_with_fl_client_func():
    """Tests the fl pipeline using the fl_client decorator"""

    @fl_client()
    def client():
        pass

    # For ease of testing, we test directly against the fl _pipeline.
    # pylint: disable-next=protected-access
    pipeline = _pipelines._pipeline(
        fl_client=client,
        registry="localhost:5000",
        verify_registry_tls=False,
    )

    argo_workflow = convert_pipeline_to_argo_workflow(pipeline)

    assert_argo_workflow_has_exit_handler(argo_workflow, "cleanup-flower-server-infrastructure")

    dag = extract_dag(argo_workflow)

    assert_task_is_setup(dag, "prepare-build-context")
    assert_task_is_setup(
        dag,
        "fl-client-image-builder",
        dependencies=["prepare-build-context"],
        parameters={"image_tag": "{{inputs.parameters.image_tag}}"},
        artifacts={
            # pylint: disable-next=line-too-long
            "prepare-build-context-build_context_path": "{{tasks.prepare-build-context.outputs.artifacts.prepare-build-context-build_context_path}}"  # noqa
        },
    )
    assert_task_is_setup(
        dag,
        "flower-server",
        parameters={
            "min_available_clients": "{{inputs.parameters.min_available_clients}}",
            "min_eval_clients": "{{inputs.parameters.min_eval_clients}}",
            "min_fit_clients": "{{inputs.parameters.min_fit_clients}}",
            "num_local_rounds": "{{inputs.parameters.num_local_rounds}}",
            "num_rounds": "{{inputs.parameters.num_rounds}}",
        },
        dependencies=["setup-flower-server-infrastructure"],
    )
    assert_task_is_setup(dag, "setup-flower-server-infrastructure")


def test_fl_pipeline_with_fl_client_context_url():
    """Tests the fl pipeline using the client context url"""

    # For ease of testing, we test directly against the fl _pipeline.
    # pylint: disable-next=protected-access
    pipeline = _pipelines._pipeline(
        fl_client_context_url="a-non-existing-context-url",
        registry="localhost:5000",
        verify_registry_tls=False,
    )

    argo_workflow = convert_pipeline_to_argo_workflow(pipeline)

    assert_argo_workflow_has_exit_handler(argo_workflow, "cleanup-flower-server-infrastructure")

    dag = extract_dag(argo_workflow)

    assert_task_is_setup(dag, "prepare-build-context")
    assert_task_is_setup(
        dag,
        "fl-client-image-builder",
        dependencies=["prepare-build-context"],
        parameters={"image_tag": "{{inputs.parameters.image_tag}}"},
        artifacts={
            # pylint: disable-next=line-too-long
            "prepare-build-context-build_context_path": "{{tasks.prepare-build-context.outputs.artifacts.prepare-build-context-build_context_path}}"  # noqa
        },
    )
    assert_task_is_setup(
        dag,
        "flower-server",
        parameters={
            "min_available_clients": "{{inputs.parameters.min_available_clients}}",
            "min_eval_clients": "{{inputs.parameters.min_eval_clients}}",
            "min_fit_clients": "{{inputs.parameters.min_fit_clients}}",
            "num_local_rounds": "{{inputs.parameters.num_local_rounds}}",
            "num_rounds": "{{inputs.parameters.num_rounds}}",
        },
        dependencies=["setup-flower-server-infrastructure"],
    )
    assert_task_is_setup(dag, "setup-flower-server-infrastructure")


def test_fl_pipeline_with_fl_client_image():
    """Tests the fl pipeline using the client image"""

    # For ease of testing, we test directly against the fl _pipeline.
    # pylint: disable-next=protected-access
    pipeline = _pipelines._pipeline(
        fl_client_image="fl_client_image:latest",
        registry="localhost:5000",
        verify_registry_tls=False,
    )

    argo_workflow = convert_pipeline_to_argo_workflow(pipeline)

    assert_argo_workflow_has_exit_handler(argo_workflow, "cleanup-flower-server-infrastructure")

    dag = extract_dag(argo_workflow)

    assert_task_is_setup(dag, "fl-client-image")
    assert_task_is_setup(
        dag,
        "flower-server",
        parameters={
            "min_available_clients": "{{inputs.parameters.min_available_clients}}",
            "min_eval_clients": "{{inputs.parameters.min_eval_clients}}",
            "min_fit_clients": "{{inputs.parameters.min_fit_clients}}",
            "num_local_rounds": "{{inputs.parameters.num_local_rounds}}",
            "num_rounds": "{{inputs.parameters.num_rounds}}",
        },
        dependencies=["setup-flower-server-infrastructure"],
    )
    assert_task_is_setup(dag, "setup-flower-server-infrastructure")


def test_correlation_pipeline():
    """Test the correlation pipeline"""

    @data(packages=["numpy"])
    def client() -> np.ndarray:
        return np.zeros(1)

    # For ease of testing, we test directly against the fl correlation_pipeline.
    # pylint: disable-next=protected-access
    pipeline = _correlation.correlation_pipeline(
        fl_client=client,
        fl_server_image="ghcr.io/katulu-io/fl-suite/analytics-server:{__version__}",
        registry="localhost:5000",
        verify_registry_tls=False,
    )

    argo_workflow = convert_pipeline_to_argo_workflow(pipeline)

    assert_argo_workflow_has_exit_handler(argo_workflow, "cleanup-flower-server-infrastructure")

    dag = extract_dag(argo_workflow)
    assert_task_is_setup(dag, "prepare-build-context")
    assert_task_is_setup(
        dag,
        "fl-client-image-builder",
        dependencies=["prepare-build-context"],
        parameters={"image_tag": "{{inputs.parameters.image_tag}}"},
        artifacts={
            # pylint: disable-next=line-too-long
            "prepare-build-context-build_context_path": "{{tasks.prepare-build-context.outputs.artifacts.prepare-build-context-build_context_path}}"  # noqa
        },
    )
    assert_task_is_setup(
        dag,
        "flower-server",
        parameters={"min_available_clients": "{{inputs.parameters.min_available_clients}}"},
        dependencies=["setup-flower-server-infrastructure"],
    )
    assert_task_is_setup(dag, "setup-flower-server-infrastructure")


def convert_pipeline_to_argo_workflow(pipeline) -> Dict[str, Any]:
    """Converts a pipeline to an argo workflow: dictionary representation"""

    compiler = Compiler()
    # _create_workflow is used to retrieve a parsed (dictionary) representation of the pipeline
    # pylint: disable-next=protected-access
    return compiler._create_workflow(pipeline)


def extract_dag(argo_workflow: Dict[str, Any]) -> Dict[Any, Any]:
    """Extracts the directed acylic graph from an argo workflow"""

    entrypoint = find_by_name(
        argo_workflow["spec"]["templates"], argo_workflow["spec"]["entrypoint"]
    )
    assert entrypoint is not None, "Entrypoint not found"

    main_task = find_by_name(
        argo_workflow["spec"]["templates"], entrypoint["dag"]["tasks"][0]["name"]
    )
    assert main_task is not None, "Main task not found"

    return main_task["dag"]


def assert_argo_workflow_has_exit_handler(argo_workflow: Dict[str, Any], exit_handler_name: str):
    """Asserts that the given argo workflow has an exit handler"""

    assert argo_workflow["spec"]["onExit"] == exit_handler_name


def assert_task_is_setup(
    dag: Dict[Any, Any],
    task_name: str,
    dependencies: Optional[List[str]] = None,
    parameters: Optional[Dict[str, str]] = None,
    artifacts: Optional[Dict[str, str]] = None,
):
    """Asserts that the given task exists in the directed acylic graph"""

    task = find_by_name(dag["tasks"], task_name)
    assert task is not None, f'"{task_name}" task not found'

    if dependencies is not None:
        assert task["dependencies"] == dependencies

    if parameters is not None:
        expected_parameters = [{"name": name, "value": value} for name, value in parameters.items()]
        assert task["arguments"]["parameters"] == expected_parameters

    if artifacts is not None:
        expected_artifacts = [{"name": name, "from": value} for name, value in artifacts.items()]
        assert task["arguments"]["artifacts"] == expected_artifacts


def find_by_name(template_list, template_name: str) -> Optional[Dict[Any, Any]]:
    """Finds a dictionary by the "name" key"""

    for template in template_list:
        if template["name"] == template_name:
            return template

    return None
