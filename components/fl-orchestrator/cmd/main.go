package main

import (
	"context"
	"flag"
	"log"
	"net"
	"time"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"

	"github.com/katulu-io/fl-suite/fl-orchestrator/pkg/client"
	v1api "github.com/katulu-io/fl-suite/fl-orchestrator/pkg/api/fl_orchestrator/v1"
	"github.com/katulu-io/fl-suite/fl-orchestrator/pkg/server"
	"github.com/katulu-io/fl-suite/fl-orchestrator/pkg/watcher"
)

func main() {
	pipelineAPIURL := flag.String("pipeline-api-url", "http://localhost:8080", "URL of the pipeline API")
	tokenFile := flag.String("token-file", "", "Path to the file containing an authorization token for the pipeline API")
	pipelineNamespace := flag.String("pipeline-namespace", "", "Namespace to query for runs in the pipeline API")
	minioEndpoint := flag.String("minio-endpoint", "localhost:9000", "URL of the pipeline API")
	minioCredentials := flag.String("minio-credentials", "/tmp/credentials", "URL of the pipeline API")
	pollIntervalFlag := flag.String("interval", "2s", "Poll interval")
	listenAddr := flag.String("addr", ":9090", "HTTP server address to listen")
	flag.Parse()

	listener, err := net.Listen("tcp", *listenAddr)
	if err != nil {
		log.Fatal(err)
	}

	srv := server.NewServer()
	var opts []grpc.ServerOption

	grpcServer := grpc.NewServer(opts...)
	v1api.RegisterFlOrchestratorServer(grpcServer, srv)
	reflection.Register(grpcServer)

	pollInterval, err := time.ParseDuration(*pollIntervalFlag)
	if err != nil {
		log.Fatal(err)
	}

	pipelineClient := client.New(*pipelineAPIURL, *pipelineNamespace)
	minioClient, err := minio.New(*minioEndpoint, &minio.Options{
		Creds:  credentials.NewFileAWSCredentials(*minioCredentials, ""),
		Secure: false,
	})
	if err != nil {
		log.Fatal(err)
	}

	watch := watcher.Watcher{
		Interval:      pollInterval,
		Client:        pipelineClient,
		MinioClient:   minioClient,
		AuthTokenFile: *tokenFile,
		GrpcServer:    srv,
	}

	ctx := context.Background()
	go watch.Run(ctx)

	log.Printf("Listening %s...", *listenAddr)
	log.Fatal(grpcServer.Serve(listener))
}
