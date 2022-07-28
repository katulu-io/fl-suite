package server

import (
	"context"
	"fmt"

	v1api "github.com/katulu-io/fl-suite/fl-orchestrator/pkg/api/fl_orchestrator/v1"
)

type FlOrchestratorServer struct {
	v1api.UnimplementedFlOrchestratorServer

	tasks []*v1api.OrchestratorMessage_TaskSpec
}

func NewServer() *FlOrchestratorServer {
	return &FlOrchestratorServer{
		tasks: make([]*v1api.OrchestratorMessage_TaskSpec, 0),
	}
}

func NewTaskSpec(runID, workflow, sni, image string) *v1api.OrchestratorMessage_TaskSpec {
	return &v1api.OrchestratorMessage_TaskSpec{
		ID:       runID,
		Workflow: workflow,
		SNI:      sni,
		Executor: &v1api.OrchestratorMessage_ExecutorSpec{
			Executor: &v1api.OrchestratorMessage_ExecutorSpec_OciExecutor{
				OciExecutor: &v1api.OrchestratorMessage_ExecutorSpec_OCIExecutorSpec{
					Image: image,
				},
			},
		},
	}
}

func (s *FlOrchestratorServer) Join(req *v1api.OperatorMessage, stream v1api.FlOrchestrator_JoinServer) error {
	message := &v1api.OrchestratorMessage{
		Tasks: s.tasks,
	}

	err := stream.Send(message)
	if err != nil {
		return fmt.Errorf("failed to send task list: %v", err)
	}

	return nil
}

func (s *FlOrchestratorServer) GetTasks(ctx context.Context, req *v1api.OperatorMessage) (*v1api.OrchestratorMessage, error) {
	return &v1api.OrchestratorMessage{
		Tasks: s.tasks,
	}, nil
}

func (s *FlOrchestratorServer) SetTasks(tasks []*v1api.OrchestratorMessage_TaskSpec) {
	s.tasks = tasks
}
