package watcher

import (
	"context"
	"log"
	"os"
	"time"

	"github.com/katulu-io/fl-suite/fl-orchestrator/pkg/client"
	"github.com/katulu-io/fl-suite/fl-orchestrator/pkg/server"

	pb "github.com/katulu-io/fl-suite/fl-orchestrator/pkg/proto"

	"github.com/minio/minio-go/v7"
)

type Watcher struct {
	Interval      time.Duration
	Client        *client.PipelineClient
	MinioClient   *minio.Client
	AuthTokenFile string
	GrpcServer    *server.FlOrchestratorServer
}

func (w *Watcher) Run(ctx context.Context) {
	for {
		func() {
			// Auth tokens can expire. New auth tokens are periodically written
			// to the auth token file. To ensure that we're using the latest one,
			// we're reading the file with each poll. For the edge case that a token
			// expires while we're in between API calls as part of a poll, we assume
			// that there's some leeway until the old auth token expires.
			authToken := ""
			if w.AuthTokenFile != "" {
				tokenBytes, err := os.ReadFile(w.AuthTokenFile)
				if err != nil {
					log.Fatal(err)
				}

				authToken = string(tokenBytes)
			}

			pollCtx, cancel := context.WithTimeout(ctx, w.Interval)
			defer cancel()

			runIDs, err := w.Client.Poll(pollCtx, authToken)
			if err != nil {
				log.Println(err)
			}

			servers := make([]*pb.ServerResponse, 0)
			for _, runID := range runIDs {
				pipelineRun, err := w.Client.GetRun(pollCtx, runID, authToken)
				if err != nil {
					log.Println(err)
					continue
				}

				workflowManifest, err := client.ParseWorkflowManifest(pipelineRun.PipelineRuntime.WorkflowManifest)
				if err != nil {
					log.Println(err)
					continue
				}

				clientImage, err := w.getRunOutput(
					pollCtx, *workflowManifest, "katulu/fl-client", "flower-client", "image_url",
				)
				if err != nil {
					log.Println(err)
					continue
				}

				serverSNI, err := w.getRunOutput(
					pollCtx, *workflowManifest, "katulu/fl-server", "infrastructure", "flower_server_sni",
				)
				if err != nil {
					log.Println(err)
					continue
				}

				server := pb.ServerResponse{
					RunID:        runID,
					WorkflowName: workflowManifest.Metadata.Name,
					ClientImage:  clientImage,
					ServerSNI:    serverSNI,
				}
				servers = append(servers, &server)
			}

			w.GrpcServer.SetServers(servers)
		}()

		select {
		case <-ctx.Done():
			return
		case <-time.After(w.Interval):
			continue
		}
	}
}

func (w *Watcher) getRunOutput(ctx context.Context, workflowManifest client.RunWorkflowManifest, labelName, labelValue, artifactName string) (string, error) {
	outputArchive, err := w.MinioClient.GetObject(
		ctx,
		"mlpipeline",
		workflowManifest.GetOutputS3Key(labelName, labelValue, artifactName),
		minio.GetObjectOptions{},
	)
	if err != nil {
		return "", err
	}
	defer outputArchive.Close()

	output, err := client.GetTaskOutputValue(outputArchive)
	if err != nil {
		return "", err
	}

	return output, nil
}
