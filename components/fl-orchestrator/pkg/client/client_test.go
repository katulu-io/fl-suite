package client_test

import (
	"archive/tar"
	"bytes"
	"compress/gzip"
	"context"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"

	"github.com/katulu-io/fl-suite/fl-orchestrator/pkg/client"
	"github.com/katulu-io/fl-suite/fl-orchestrator/pkg/fixtures"
)

type PollTestCase struct {
	name           string
	respStatusCode int
	respBody       string
	expectedRunIDs []string
}

type GetRunTestCase struct {
	name           string
	runID          string
	respStatusCode int
	respBody       string
	expectedError  bool
	expectedServer client.RunResponse
}

func TestPoll(t *testing.T) {
	testCases := []PollTestCase{
		{
			name:           "Empty runs response",
			respStatusCode: http.StatusOK,
			respBody:       `{"runs":[],"total_size":0}`,
			expectedRunIDs: []string{},
		},
		{
			name:           "Many runs but no fl-server found",
			respStatusCode: http.StatusOK,
			respBody:       fixtures.RunsResponseNoFLServer,
			expectedRunIDs: []string{},
		},
		{
			name:           "fl-server found",
			respStatusCode: http.StatusOK,
			respBody:       fixtures.RunsResponseOneFLServer,
			expectedRunIDs: []string{"12345678-5432-4755-a58b-c99b54189e6a"},
		},
	}

	for _, testCase := range testCases {
		t.Log(testCase.name)

		func(testCase PollTestCase) {
			testServer := httptest.NewServer(http.HandlerFunc(func(res http.ResponseWriter, req *http.Request) {
				res.WriteHeader(testCase.respStatusCode)
				_, err := res.Write([]byte(testCase.respBody))
				if err != nil {
					t.Fatal(err)
				}
			}))
			defer func() { testServer.Close() }()

			pc := client.New(testServer.URL, "")
			runIDs, err := pc.Poll(context.Background(), "")
			if err != nil {
				t.Fatal(err)
			}

			if !reflect.DeepEqual(runIDs, testCase.expectedRunIDs) {
				t.Fatalf(`Expected run ID: "%s", got "%s"`, testCase.expectedRunIDs, runIDs)
			}
		}(testCase)
	}
}

func TestGetRun(t *testing.T) {
	testCases := []GetRunTestCase{
		{
			name:           "Run response with workflow manifest",
			runID:          "test-run-id",
			respStatusCode: http.StatusOK,
			respBody:       fixtures.RunResponseWithWorkflowManifest,
			expectedError:  false,
			expectedServer: client.RunResponse{
				Run: struct {
					ID           string `json:"id"`
					Name         string `json:"name"`
					PipelineSpec struct {
						WorkflowManifest string `json:"workflow_manifest"`
					} `json:"pipeline_spec"`
				}{
					ID:   "fa05261f-4d37-4d51-821b-0bc76b5825da",
					Name: "Run of pipeline (59130)",
				},
				PipelineRuntime: struct {
					WorkflowManifest string `json:"workflow_manifest"`
				}{
					WorkflowManifest: "{ \"metadata\": { \"name\": \"create-fl-client-image-4jx7c\" }, \"status\": { \"nodes\": { \"create-fl-client-image-4jx7c-2015089401\": { \"templateName\": \"fl-client-image-builder\", \"outputs\": { \"artifacts\": [ { \"name\": \"fl-client-image-builder-image_url\", \"path\": \"/tmp/outputs/output/data\", \"s3\": { \"key\": \"artifacts/pod-name/fl-client-image-builder-image_url.tgz\" } }, { \"name\": \"main-logs\", \"s3\": { \"key\": \"artifacts/pod-name/main.log\" } } ] } } } } }",
				},
			},
		},
		{
			name:           "Run response with empty workflow manifest",
			runID:          "test-run-id",
			respStatusCode: http.StatusOK,
			respBody:       fixtures.RunResponseWithEmptyWorkflowManifest,
			expectedError:  false,
			expectedServer: client.RunResponse{
				Run: struct {
					ID           string `json:"id"`
					Name         string `json:"name"`
					PipelineSpec struct {
						WorkflowManifest string `json:"workflow_manifest"`
					} `json:"pipeline_spec"`
				}{
					ID:   "97ee331f-7d26-4755-a58b-c99b54189e6a",
					Name: "Run of pipeline (95301)",
				},
				PipelineRuntime: struct {
					WorkflowManifest string `json:"workflow_manifest"`
				}{
					WorkflowManifest: "",
				},
			},
		},
	}

	for _, testCase := range testCases {
		t.Log(testCase.name)

		func(testCase GetRunTestCase) {
			testServer := httptest.NewServer(http.HandlerFunc(func(res http.ResponseWriter, req *http.Request) {
				res.WriteHeader(testCase.respStatusCode)
				_, err := res.Write([]byte(testCase.respBody))
				if err != nil {
					t.Fatal(err)
				}
			}))
			defer func() { testServer.Close() }()

			c := client.New(testServer.URL, "")
			run, err := c.GetRun(context.Background(), testCase.runID, "")
			if err != nil && !testCase.expectedError {
				t.Fatal(err)
			}

			if !reflect.DeepEqual(run, testCase.expectedServer) {
				t.Logf("Expectation: %+v\n", testCase.expectedServer)
				t.Logf("Output: %+v\n", run)
				t.Fatal("Run doesn't match expectation")
			}
		}(testCase)
	}
}

func TestGetOutputS3Key(t *testing.T) {
	testCases := []GetOutputS3KeyTestCase{
		{
			name:             "Empty RunWorkflowManifest returns empty s3Key",
			workflowManifest: client.RunWorkflowManifest{},
			labelName:        "katulu/fl-client",
			labelValue:       "flower-client",
			artifactToFind:   "output",
			expected:         "",
		},
		// Where is your God now (nested struct of a nested struct of a nested struct ...)?!
		{
			name: "RunWorkflowManifest finds s3Key",
			workflowManifest: client.RunWorkflowManifest{
				Metadata: struct {
					Name string `json:"name"`
				}{
					Name: "test",
				},
				Spec: struct {
					Templates []struct {
						Name     string `json:"name"`
						MetaData struct {
							Labels map[string]string `json:"labels"`
						} `json:"metadata"`
					} `json:"templates"`
				}{
					Templates: []struct {
						Name     string `json:"name"`
						MetaData struct {
							Labels map[string]string `json:"labels"`
						} `json:"metadata"`
					}{
						{
							Name: "task-1",
							MetaData: struct {
								Labels map[string]string `json:"labels"`
							}{
								Labels: map[string]string{
									"katulu/fl-client": "flower-client",
								},
							},
						},
					},
				},
				Status: struct {
					Nodes map[string]struct {
						TemplateName string "json:\"templateName\""
						Outputs      struct {
							Artifacts []struct {
								Name string "json:\"name\""
								Path string "json:\"path\""
								S3   struct {
									Key string "json:\"key\""
								} "json:\"s3\""
							} "json:\"artifacts\""
						} "json:\"outputs\""
					}
				}{
					Nodes: map[string]struct {
						TemplateName string "json:\"templateName\""
						Outputs      struct {
							Artifacts []struct {
								Name string "json:\"name\""
								Path string "json:\"path\""
								S3   struct {
									Key string "json:\"key\""
								} "json:\"s3\""
							} "json:\"artifacts\""
						} "json:\"outputs\""
					}{
						"test-task": {
							TemplateName: "task-1",
							Outputs: struct {
								Artifacts []struct {
									Name string "json:\"name\""
									Path string "json:\"path\""
									S3   struct {
										Key string "json:\"key\""
									} "json:\"s3\""
								} "json:\"artifacts\""
							}{
								Artifacts: []struct {
									Name string "json:\"name\""
									Path string "json:\"path\""
									S3   struct {
										Key string "json:\"key\""
									} "json:\"s3\""
								}{
									{
										Name: "task-1-output",
										Path: "/tmp/outputs/output/data",
										S3: struct {
											Key string "json:\"key\""
										}{
											Key: "artifacts/pod-name/task-1-output.tgz",
										},
									},
								},
							},
						},
					},
				},
			},
			labelName:      "katulu/fl-client",
			labelValue:     "flower-client",
			artifactToFind: "output",
			expected:       "artifacts/pod-name/task-1-output.tgz",
		},
	}

	for _, testCase := range testCases {
		t.Log(testCase.name)

		func(testCase GetOutputS3KeyTestCase) {
			s3Key := testCase.workflowManifest.GetOutputS3Key(testCase.labelName, testCase.labelValue, testCase.artifactToFind)

			if s3Key != testCase.expected {
				t.Logf("Expectation: %s\n", testCase.expected)
				t.Logf("Output: %s\n", s3Key)
				t.Fatal("Output doesn't match expectation")
			}
		}(testCase)
	}
}

type GetOutputS3KeyTestCase struct {
	name             string
	workflowManifest client.RunWorkflowManifest
	labelName        string
	labelValue       string
	artifactToFind   string
	expected         string
}

func TestGetOutput(t *testing.T) {
	testCases := []GetOutputTestCase{
		{
			name: "Get output content from archive",
			archive: createOutputArchive(
				t, map[string]string{
					"data": "container-registry.example.com/image:latest\n",
				},
			),
			expectedError:  false,
			expectedOutput: "container-registry.example.com/image:latest",
		},
		{
			name:           "Err with empty archive",
			archive:        createOutputArchive(t, map[string]string{}),
			expectedError:  true,
			expectedOutput: "",
		},
		{
			name:           "Err with plain file",
			archive:        bytes.NewBufferString("container-registry.example.com/image:latest"),
			expectedError:  true,
			expectedOutput: "",
		},
	}

	for _, testCase := range testCases {
		t.Log(testCase.name)

		func(testCase GetOutputTestCase) {
			output, err := client.GetTaskOutputValue(testCase.archive)
			if err != nil && !testCase.expectedError {
				t.Log("Unexpected error")
				t.Fatal(err)
			} else if err == nil && testCase.expectedError {
				t.Fatal(fmt.Errorf("Missing expected error"))
			}

			if output != testCase.expectedOutput {
				t.Logf("Expectation: %s\n", testCase.expectedOutput)
				t.Logf("Output: %s\n", output)
				t.Fatal("Output doesn't match expectation")
			}
		}(testCase)
	}
}

func createOutputArchive(t *testing.T, fileContentMapping map[string]string) io.Reader {
	tarFile := new(bytes.Buffer)

	gz := gzip.NewWriter(tarFile)
	defer gz.Close()
	tw := tar.NewWriter(gz)
	defer tw.Close()

	for filename, content := range fileContentMapping {
		tarHeader := &tar.Header{
			Name: filename,
			Mode: 0600,
			Size: int64(len(content)),
		}
		if err := tw.WriteHeader(tarHeader); err != nil {
			t.Fatal(err)
			return nil
		}
		if _, err := tw.Write([]byte(content)); err != nil {
			t.Fatal(err)
			return nil
		}
	}

	return tarFile
}

type GetOutputTestCase struct {
	name           string
	archive        io.Reader
	expectedError  bool
	expectedOutput string
}
