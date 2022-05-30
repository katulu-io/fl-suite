package server

import (
	"context"
	"fmt"

	pb "github.com/katulu-io/fl-suite/fl-orchestrator/pkg/proto"
)

type FlOrchestratorServer struct {
	pb.UnimplementedFlOrchestratorServer

	servers []*pb.ServerResponse
}

func NewServer() *FlOrchestratorServer {
	servers := make([]*pb.ServerResponse, 0)

	return &FlOrchestratorServer{
		servers: servers,
	}
}

func (s *FlOrchestratorServer) ListServers(req *pb.ServersRequest, stream pb.FlOrchestrator_ListServersServer) error {
	for _, server := range s.servers {
		err := stream.Send(server)

		if err != nil {
			return fmt.Errorf("failed to send server list: %v", err)
		}
	}

	return nil
}

func (s *FlOrchestratorServer) GetServers(ctx context.Context, req *pb.ServersRequest) (*pb.GetServersResponse, error) {
	return &pb.GetServersResponse{
		Servers: s.servers,
	}, nil
}

func (s *FlOrchestratorServer) SetServers(servers []*pb.ServerResponse) {
	s.servers = servers
}

func (s *FlOrchestratorServer) AddServer(newServer *pb.ServerResponse) error {
	for _, server := range s.servers {
		if server.RunID == newServer.RunID {
			return fmt.Errorf("failed to add server: server with runID %s already stored", server.RunID)
		}
	}

	s.servers = append(s.servers, newServer)

	return nil
}
