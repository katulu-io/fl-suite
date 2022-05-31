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

	tasks []*pb.OrchestratorMessage_TaskSpec
}

func (m *mockOrchestratorServer) Join(req *pb.OperatorMessage, stream pb.FlOrchestrator_JoinServer) error {
	message := &pb.OrchestratorMessage{
		Message: &pb.OrchestratorMessage_Tasks{
			Tasks: &pb.OrchestratorMessage_TasksSpec{
				Tasks: m.tasks,
			},
		},
	}

	err := stream.Send(message)
	if err != nil {
		return err
	}

	return nil
}

func (m *mockOrchestratorServer) GetTasks(ctx context.Context, req *pb.OperatorMessage) (*pb.OrchestratorMessage, error) {
	return &pb.OrchestratorMessage{
		Message: &pb.OrchestratorMessage_Tasks{
			Tasks: &pb.OrchestratorMessage_TasksSpec{
				Tasks: m.tasks,
			},
		},
	}, nil
}

func dialer(tasks []*pb.OrchestratorMessage_TaskSpec) func(context.Context, string) (net.Conn, error) {
	listener := bufconn.Listen(1024 * 1024)

	server := grpc.NewServer()

	pb.RegisterFlOrchestratorServer(server, &mockOrchestratorServer{
		tasks: tasks,
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
	Describe("GetTasks", func() {
		It("should return an empty array of tasks", func() {
			ctx := context.Background()
			emptyResponse := make([]*pb.OrchestratorMessage_TaskSpec, 0)
			conn, err := grpc.DialContext(ctx, "", grpc.WithTransportCredentials(insecure.NewCredentials()), grpc.WithContextDialer(dialer(emptyResponse)))
			Expect(err).ToNot(HaveOccurred())
			defer conn.Close()

			timeout := time.Second * 3

			cl := client.NewClient(conn, timeout)

			response, err := cl.GetTasks(context.Background())

			Expect(err).ToNot(HaveOccurred())
			Expect(len(response.GetTasks().Tasks)).To(Equal(0))
		})

		It("should return a non-empty array of tasks", func() {
			ctx := context.Background()
			nonEmptyResponse := []*pb.OrchestratorMessage_TaskSpec{
				{
					ID:       "test-run-id-1",
					SNI:      "test.server-1.io",
					Workflow: "test-workflow-1",
					Executor: &pb.OrchestratorMessage_ExecutorSpec{
						Executor: &pb.OrchestratorMessage_ExecutorSpec_OciExecutor{
							OciExecutor: &pb.OrchestratorMessage_ExecutorSpec_OCIExecutorSpec{
								Image: "test/image-1:0.1",
							},
						},
					},
				},
				{
					ID:       "test-run-id-2",
					SNI:      "test.server-2.io",
					Workflow: "test-workflow-2",
					Executor: &pb.OrchestratorMessage_ExecutorSpec{
						Executor: &pb.OrchestratorMessage_ExecutorSpec_OciExecutor{
							OciExecutor: &pb.OrchestratorMessage_ExecutorSpec_OCIExecutorSpec{
								Image: "test/image-2:0.1",
							},
						},
					},
				},
			}
			conn, err := grpc.DialContext(ctx, "", grpc.WithTransportCredentials(insecure.NewCredentials()), grpc.WithContextDialer(dialer(nonEmptyResponse)))
			Expect(err).ToNot(HaveOccurred())
			defer conn.Close()

			timeout := time.Second * 3

			cl := client.NewClient(conn, timeout)

			response, err := cl.GetTasks(context.Background())

			Expect(err).ToNot(HaveOccurred())
			tasks := response.GetTasks().Tasks
			Expect(len(tasks)).To(Equal(2))
			Expect(tasks[0].ID).To(Equal("test-run-id-1"))
			Expect(tasks[0].SNI).To(Equal("test.server-1.io"))
			Expect(tasks[0].Workflow).To(Equal("test-workflow-1"))
			Expect(tasks[0].Executor.GetOciExecutor().Image).To(Equal("test/image-1:0.1"))
			Expect(tasks[1].ID).To(Equal("test-run-id-2"))
			Expect(tasks[1].SNI).To(Equal("test.server-2.io"))
			Expect(tasks[1].Workflow).To(Equal("test-workflow-2"))
			Expect(tasks[1].Executor.GetOciExecutor().Image).To(Equal("test/image-2:0.1"))
		})
	})
})
