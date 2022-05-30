package client

import (
	"archive/tar"
	"compress/gzip"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
)

const (
	FL_SERVER_LABEL_KEY = "katulu/fl-server"
	FL_SERVER_LABEL_VAL = "flower-server"

	FL_CLIENT_LABEL_KEY = "katulu/fl-client"
	FL_CLIENT_LABEL_VAL = "flower-client"

	RUNS_URL    = "apis/v1beta1/runs"
	RUNS_FILTER = `{"predicates":[{"key":"status","op":"EQUALS","string_value":"Running"}]}`
)

type RunsResponse struct {
	Runs      []run `json:"runs"`
	TotalSize int   `json:"total_size"`
}

type RunWorkflowManifest struct {
	Metadata struct {
		Name string `json:"name"`
	} `json:"metadata"`
	Spec struct {
		Templates []struct {
			Name     string `json:"name"`
			MetaData struct {
				Labels map[string]string `json:"labels"`
			} `json:"metadata"`
		} `json:"templates"`
	} `json:"spec"`
	Status struct {
		Nodes map[string]struct {
			TemplateName string `json:"templateName"`
			Outputs      struct {
				Artifacts []struct {
					Name string `json:"name"`
					Path string `json:"path"`
					S3   struct {
						Key string `json:"key"`
					} `json:"s3"`
				} `json:"artifacts"`
			} `json:"outputs"`
		}
	} `json:"status"`
}

type RunResponse struct {
	Run             run `json:"run"`
	PipelineRuntime struct {
		WorkflowManifest string `json:"workflow_manifest"`
	} `json:"pipeline_runtime"`
}

type run struct {
	ID           string `json:"id"`
	Name         string `json:"name"`
	PipelineSpec struct {
		WorkflowManifest string `json:"workflow_manifest"`
	} `json:"pipeline_spec"`
}

type PipelineClient struct {
	baseURL           string
	pipelineNamespace string
	httpClient        *http.Client
}

func New(baseURL string, pipelineNamespace string) *PipelineClient {
	return &PipelineClient{
		baseURL:           baseURL,
		pipelineNamespace: pipelineNamespace,
		httpClient:        &http.Client{},
	}
}

func ParseWorkflowManifest(workflowManifestJSON string) (*RunWorkflowManifest, error) {
	manifest := RunWorkflowManifest{}

	err := json.Unmarshal([]byte(workflowManifestJSON), &manifest)
	if err != nil {
		return nil, fmt.Errorf("failed to parse workflow manifest: %v", err)
	}

	return &manifest, nil
}

func hasFLServer(manifest *RunWorkflowManifest) bool {
	for _, template := range manifest.Spec.Templates {
		if val, ok := template.MetaData.Labels[FL_SERVER_LABEL_KEY]; ok && val == FL_SERVER_LABEL_VAL {
			return true
		}
	}

	return false
}

func findFLServer(runsResponse RunsResponse) ([]string, error) {
	runIDs := make([]string, 0)

	for _, run := range runsResponse.Runs {
		manifest, err := ParseWorkflowManifest(run.PipelineSpec.WorkflowManifest)
		if err != nil {
			return []string{}, err
		}

		if hasFLServer(manifest) {
			runIDs = append(runIDs, run.ID)
		}
	}

	return runIDs, nil
}

// Poll checks the pipeline API's /runs and returns the run ID if it finds a run that contains a label "katulu/fl-server": "flower-server"
func (c *PipelineClient) Poll(ctx context.Context, authToken string) ([]string, error) {
	base, err := url.Parse(fmt.Sprintf("%s/%s", c.baseURL, RUNS_URL))
	if err != nil {
		return []string{}, fmt.Errorf("failed to parse pipeline URL: %v", err)
	}

	params := url.Values{}
	params.Add("resource_reference_key.type", "NAMESPACE")
	params.Add("resource_reference_key.id", c.pipelineNamespace)
	params.Add("filter", RUNS_FILTER)
	base.RawQuery = params.Encode()
	url := base.String()

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return []string{}, fmt.Errorf("failed to GET pipeline runs: %v", err)
	}

	if authToken != "" {
		req.Header.Add("Authorization", "Bearer "+authToken)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return []string{}, fmt.Errorf("pipeline runs failed to respond: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return []string{}, fmt.Errorf("failed to read pipeline runs response: %v", err)
	}

	runsResponse := RunsResponse{}
	err = json.Unmarshal(body, &runsResponse)
	if err != nil {
		return []string{}, fmt.Errorf("failed to unmarshal pipeline runs response: %v", err)
	}

	runIDs, err := findFLServer(runsResponse)
	if err != nil {
		return []string{}, fmt.Errorf("failed to extract FL server runs from pipeline runs response: %v", err)
	}

	return runIDs, nil
}

// GetRun gets the run from /runs/{runID}
func (c *PipelineClient) GetRun(ctx context.Context, runID string, authToken string) (RunResponse, error) {
	url := fmt.Sprintf("%s/%s/%s", c.baseURL, RUNS_URL, runID)

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return RunResponse{}, fmt.Errorf("failed to GET run '%s': %v", runID, err)
	}

	if authToken != "" {
		req.Header.Add("Authorization", "Bearer "+authToken)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return RunResponse{}, fmt.Errorf("pipeline run '%s' failed to respond: %v", runID, err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return RunResponse{}, fmt.Errorf("failed to read response of pipeline run '%s': %v", runID, err)
	}

	runResponse := RunResponse{}
	err = json.Unmarshal(body, &runResponse)
	if err != nil {
		return RunResponse{}, fmt.Errorf("failed to unmarshal response of pipeline run '%s': %v", runID, err)
	}

	return runResponse, nil
}

func (r *RunWorkflowManifest) GetOutputS3Key(labelName, labelValue, artifactName string) string {
	templateName := ""

	for _, template := range r.Spec.Templates {
		if val, ok := template.MetaData.Labels[labelName]; ok && val == labelValue {
			templateName = template.Name
			break
		}
	}

	for _, node := range r.Status.Nodes {
		if node.TemplateName == templateName {
			for _, artifact := range node.Outputs.Artifacts {
				if artifact.Name == templateName+"-"+artifactName {
					return artifact.S3.Key
				}
			}
		}
	}

	return ""
}

// The reader is a tar.gz file with a single "data" file that contains the task output
func GetTaskOutputValue(reader io.Reader) (string, error) {
	gzipReader, err := gzip.NewReader(reader)
	if err != nil {
		return "", fmt.Errorf("failed to create task output data reader: %v", err)
	}
	defer gzipReader.Close()

	tarReader := tar.NewReader(gzipReader)

	// Assuming that output tgz contains a single "data" file
	_, err = tarReader.Next()
	if err != nil {
		return "", fmt.Errorf("failed to read task output data file: %v", err)
	}

	stringBuffer := &strings.Builder{}
	_, err = io.Copy(stringBuffer, tarReader)
	if err != nil {
		return "", fmt.Errorf("failed to copy task output data: %v", err)
	}

	return strings.Trim(stringBuffer.String(), "\n "), nil
}
