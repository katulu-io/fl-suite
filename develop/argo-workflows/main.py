import requests
import yaml
from argo_workflows import ApiClient, Configuration
from argo_workflows.api.workflow_service_api import WorkflowServiceApi
from argo_workflows.model.io_argoproj_workflow_v1alpha1_workflow_create_request import \
    IoArgoprojWorkflowV1alpha1WorkflowCreateRequest


def main():
    config = Configuration(host="https://localhost:30046")
    config.verify_ssl = False
    api_client = ApiClient(config)
    service = WorkflowServiceApi(api_client)

    # resp = requests.get('https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples/hello-world.yaml')
    # manifest = yaml.safe_load(resp.text)
    # api_response = service.create_workflow(
    #     namespace="argo",
    #     body=IoArgoprojWorkflowV1alpha1WorkflowCreateRequest(workflow=manifest, _check_type=False),
    #     _check_return_type=False
    # )

    with open("pipeline.yaml") as f:
        manifest: dict = yaml.safe_load(f)
    del manifest['spec']['serviceAccountName']
    service.create_workflow(
        namespace='argo',
        body=IoArgoprojWorkflowV1alpha1WorkflowCreateRequest(workflow=manifest, _check_type=False),
        _check_return_type=False
    )

if __name__ == '__main__':
    main()
