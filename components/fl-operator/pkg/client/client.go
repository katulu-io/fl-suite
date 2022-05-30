package client

import (
	"context"
	"io"
	"log"
	"time"

	pb "github.com/katulu-io/fl-suite/fl-orchestrator/pkg/proto"
	"google.golang.org/grpc"
)

type Client struct {
	client  pb.FlOrchestratorClient
	timeout time.Duration
}

func NewClient(conn *grpc.ClientConn, timeout time.Duration) Client {
	client := pb.NewFlOrchestratorClient(conn)

	return Client{
		client:  client,
		timeout: timeout,
	}
}

func (c *Client) GetServers(parentCtx context.Context) (*pb.GetServersResponse, error) {
	ctx, cancel := context.WithTimeout(parentCtx, c.timeout)
	defer cancel()

	return c.client.GetServers(ctx, &pb.ServersRequest{})
}

func (c *Client) GetListServersStream(parentCtx context.Context, serverAddress string, timeout time.Duration) (*pb.FlOrchestrator_ListServersClient, error) {
	ctx, cancel := context.WithTimeout(parentCtx, c.timeout)
	defer cancel()

	stream, err := c.client.ListServers(ctx, &pb.ServersRequest{})
	if err != nil {
		return nil, err
	}

	return &stream, nil
}

func (c *Client) ListServers(parentCtx context.Context) ([]*pb.ServerResponse, error) {
	ctx, cancel := context.WithTimeout(parentCtx, c.timeout)
	defer cancel()

	stream, err := c.client.ListServers(ctx, &pb.ServersRequest{})
	if err != nil {
		return nil, err
	}

	servers := make([]*pb.ServerResponse, 0)

	for {
		server, err := stream.Recv()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Println(err)
			continue
		}

		servers = append(servers, server)
	}

	return servers, nil
}
