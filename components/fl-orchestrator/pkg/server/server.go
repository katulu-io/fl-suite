package server

import (
	"context"
	"fmt"

	pb "github.com/katulu-io/fl-suite/fl-orchestrator/pkg/proto"
)

type FlOrchestratorServer struct {
	pb.UnimplementedFlOrchestratorServer

	tasks *pb.OrchestratorMessage_TasksSpec
}

func NewServer() *FlOrchestratorServer {
	return &FlOrchestratorServer{
		tasks: &pb.OrchestratorMessage_TasksSpec{
			Tasks: make([]*pb.OrchestratorMessage_TaskSpec, 0),
		},
	}
}

func NewTaskSpec(runID, workflow, sni, image string) *pb.OrchestratorMessage_TaskSpec {
	return &pb.OrchestratorMessage_TaskSpec{
		ID:       runID,
		Workflow: workflow,
		SNI:      sni,
		Executor: &pb.OrchestratorMessage_ExecutorSpec{
			Executor: &pb.OrchestratorMessage_ExecutorSpec_OciExecutor{
				OciExecutor: &pb.OrchestratorMessage_ExecutorSpec_OCIExecutorSpec{
					Image: image,
				},
			},
		},
	}
}

func (s *FlOrchestratorServer) Join(req *pb.OperatorMessage, stream pb.FlOrchestrator_JoinServer) error {
	message := &pb.OrchestratorMessage{
		Message: &pb.OrchestratorMessage_Tasks{
			Tasks: s.tasks,
		},
	}

	err := stream.Send(message)
	if err != nil {
		return fmt.Errorf("failed to send task list: %v", err)
	}

	return nil
}

func (s *FlOrchestratorServer) GetTasks(ctx context.Context, req *pb.OperatorMessage) (*pb.OrchestratorMessage, error) {
	return &pb.OrchestratorMessage{
		Message: &pb.OrchestratorMessage_Tasks{
			Tasks: s.tasks,
		},
	}, nil
}

func (s *FlOrchestratorServer) SetTasks(tasks []*pb.OrchestratorMessage_TaskSpec) {
	s.tasks.Tasks = tasks
}
