package client_test

import (
	"context"
	"log"
	"net"
	"time"

	"github.com/katulu-io/fl-suite/fl-operator/pkg/client"
	pb "github.com/katulu-io/fl-suite/fl-orchestrator/pkg/proto"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/test/bufconn"
)

type mockOrchestratorServer struct {
	pb.UnimplementedFlOrchestratorServer

	servers []*pb.ServerResponse
}

func (m *mockOrchestratorServer) ListServers(req *pb.ServersRequest, stream pb.FlOrchestrator_ListServersServer) error {
	for _, server := range m.servers {
		err := stream.Send(server)

		if err != nil {
			return err
		}
	}

	return nil
}

func (m *mockOrchestratorServer) GetServers(ctx context.Context, req *pb.ServersRequest) (*pb.GetServersResponse, error) {
	return &pb.GetServersResponse{
		Servers: m.servers,
	}, nil
}

func dialer(servers []*pb.ServerResponse) func(context.Context, string) (net.Conn, error) {
	listener := bufconn.Listen(1024 * 1024)

	server := grpc.NewServer()

	pb.RegisterFlOrchestratorServer(server, &mockOrchestratorServer{
		servers: servers,
	})

	go func() {
		if err := server.Serve(listener); err != nil {
			log.Fatal(err)
		}
	}()

	return func(context.Context, string) (net.Conn, error) {
		return listener.Dial()
	}
}

var _ = Describe("Client", func() {
	Describe("GetServers", func() {
		It("should return an empty array of servers", func() {
			ctx := context.Background()
			emptyResponse := make([]*pb.ServerResponse, 0)
			conn, err := grpc.DialContext(ctx, "", grpc.WithTransportCredentials(insecure.NewCredentials()), grpc.WithContextDialer(dialer(emptyResponse)))
			Expect(err).ToNot(HaveOccurred())
			defer conn.Close()

			timeout := time.Second * 3

			cl := client.NewClient(conn, timeout)

			response, err := cl.GetServers(context.Background())

			Expect(err).ToNot(HaveOccurred())
			Expect(len(response.Servers)).To(Equal(0))
		})

		It("should return a non-empty map of servers", func() {
			ctx := context.Background()
			nonEmptyResponse := []*pb.ServerResponse{
				{
					RunID:        "test-run-id-1",
					WorkflowName: "test-workflow-1",
					ClientImage:  "test/image-1:0.1",
					ServerSNI:    "test.server-1.io",
				},
				{
					RunID:        "test-run-id-2",
					WorkflowName: "test-workflow-2",
					ClientImage:  "test/image-2:0.1",
					ServerSNI:    "test.server-2.io",
				},
			}
			conn, err := grpc.DialContext(ctx, "", grpc.WithTransportCredentials(insecure.NewCredentials()), grpc.WithContextDialer(dialer(nonEmptyResponse)))
			Expect(err).ToNot(HaveOccurred())
			defer conn.Close()

			timeout := time.Second * 3

			cl := client.NewClient(conn, timeout)

			response, err := cl.GetServers(context.Background())

			Expect(err).ToNot(HaveOccurred())
			Expect(len(response.Servers)).To(Equal(2))
			Expect(response.Servers[0].RunID).To(Equal("test-run-id-1"))
			Expect(response.Servers[0].WorkflowName).To(Equal("test-workflow-1"))
			Expect(response.Servers[0].ClientImage).To(Equal("test/image-1:0.1"))
			Expect(response.Servers[0].ServerSNI).To(Equal("test.server-1.io"))
			Expect(response.Servers[1].RunID).To(Equal("test-run-id-2"))
			Expect(response.Servers[1].WorkflowName).To(Equal("test-workflow-2"))
			Expect(response.Servers[1].ClientImage).To(Equal("test/image-2:0.1"))
			Expect(response.Servers[1].ServerSNI).To(Equal("test.server-2.io"))
		})
	})
})
