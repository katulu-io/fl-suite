import flwr

from client import CorrelationClient

if __name__ == "__main__":
    client = CorrelationClient()

    flwr.client.start_client(server_address="localhost:9080", client=client)
