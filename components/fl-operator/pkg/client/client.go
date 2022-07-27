package client

import (
	"context"
	"io"
	"log"
	"time"

	pb "github.com/katulu-io/fl-suite/fl-orchestrator/pkg/api/fl_orchestrator/v1"
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

func (c *Client) GetTasks(parentCtx context.Context) (*pb.OrchestratorMessage, error) {
	ctx, cancel := context.WithTimeout(parentCtx, c.timeout)
	defer cancel()

	return c.client.GetTasks(ctx, &pb.OperatorMessage{})
}

func (c *Client) GetJoinStream(parentCtx context.Context, serverAddress string, timeout time.Duration) (*pb.FlOrchestrator_JoinClient, error) {
	ctx, cancel := context.WithTimeout(parentCtx, c.timeout)
	defer cancel()

	stream, err := c.client.Join(ctx, &pb.OperatorMessage{})
	if err != nil {
		return nil, err
	}

	return &stream, nil
}

func (c *Client) Join(parentCtx context.Context) ([]*pb.OrchestratorMessage, error) {
	ctx, cancel := context.WithTimeout(parentCtx, c.timeout)
	defer cancel()

	stream, err := c.client.Join(ctx, &pb.OperatorMessage{})
	if err != nil {
		return nil, err
	}

	messages := make([]*pb.OrchestratorMessage, 0)

	for {
		message, err := stream.Recv()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Println(err)
			continue
		}

		messages = append(messages, message)
	}

	return messages, nil
}
