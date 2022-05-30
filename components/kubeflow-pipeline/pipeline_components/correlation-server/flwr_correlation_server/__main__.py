import argparse
import io
import json
import os
from pathlib import Path

import flwr
import matplotlib.pyplot as plt
from flwr.server.client_manager import SimpleClientManager

from server import CorrelationServer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--num-rounds",
        type=int,
        default=1,
        help="Number of rounds of federated learning",
    )
    parser.add_argument(
        "--num-local-rounds",
        type=int,
        default=1,
        help="Number of rounds on each client before each federated learning round",
    )
    parser.add_argument(
        "--min-available-clients",
        type=int,
        default=2,
        help="Minimal number of clients to participate in federated learning",
    )
    parser.add_argument(
        "--min-fit-clients",
        type=int,
        default=2,
        help="Minimal number of clients to participate in training",
    )
    parser.add_argument(
        "--min-eval-clients",
        type=int,
        default=2,
        help="Minimal number of clients to participate in evaluation",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        help="Path to the folder where the model weights and metrics of each training round will be written",
    )
    parser.add_argument(
        "--metadata-output-path",
        type=str,
        help="Path to the file containing JSON metadata",
    )
    args = parser.parse_args()

    client_manager = SimpleClientManager()
    server = CorrelationServer(client_manager, args.min_available_clients)

    flwr.server.start_server(server=server, config={"num_rounds": 1})

    print("correlation completed, preparing output")

    # The output paths might not exist yet.
    # In that case create it.
    Path(args.output_path).mkdir(parents=True, exist_ok=True)

    data_filepath = os.path.join(args.output_path, "data.csv")

    fig_svg = io.BytesIO()

    fig, ax = plt.subplots()
    ax.matshow(server.correlation)

    plt.savefig(fig_svg, format="svg")

    # Write Kubeflow pipeline metadata
    metadata = {
        "version": 1,
        "outputs": [
            {
                "type": "web-app",
                "storage": "inline",
                "source": fig_svg.getvalue().decode("utf-8"),
            },
        ],
    }

    Path(args.metadata_output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(args.metadata_output_path).write_text(json.dumps(metadata))
