import argparse
import io
import json
import os
from pathlib import Path

import flwr
import numpy as np
import pandas as pd

from strategy import FedAvgStoreModelStrategy

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--num-rounds",
        type=int,
        default=10,
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
        "--initial-weights-file",
        type=str,
        help="Local file containing the inital model weights",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        help="Path to the folder where the model weights of each training round will be written",
    )
    parser.add_argument(
        "--metadata-output-path",
        type=str,
        help="Path to the file containing JSON metadata",
    )
    args = parser.parse_args()

    strategy = FedAvgStoreModelStrategy(
        local_epochs=args.num_local_rounds,
        min_fit_clients=args.min_fit_clients,
        min_eval_clients=args.min_eval_clients,
        min_available_clients=args.min_available_clients,
    )

    flwr.server.start_server(config={"num_rounds": args.num_rounds}, strategy=strategy)

    # The output paths might not exist yet.
    # In that case create it.
    Path(args.output_path).mkdir(parents=True, exist_ok=True)

    # Store resulting averaged weight
    with open(
        os.path.join(args.output_path, f"weights-{args.num_rounds}.npy"), "wb"
    ) as file:
        np.save(file, strategy.weights[-1])

    # Prepare client result data
    data = []
    for run_index, metrics in enumerate(strategy.metrics):
        for cid, metric in metrics.items():
            data.append(
                [
                    run_index,
                    cid,
                    # Use 'get' to ensure empty values if a key isn't set
                    metric.get("accuracy"),
                    metric.get("precision"),
                    metric.get("recall"),
                    metric.get("examples"),
                ]
            )

    df = pd.DataFrame(
        data,
        columns=["run", "client_id", "accuracy", "precision", "recall", "num_examples"],
    )

    metrics_csv = io.BytesIO()
    df.to_csv(metrics_csv, header=False, index=False)

    # Write Kubeflow pipeline metadata
    metadata = {
        "version": 1,
        "outputs": [
            {
                "type": "table",
                "format": "csv",
                "header": [
                    "run",
                    "client_id",
                    "accuracy",
                    "precision",
                    "recall",
                    "num_examples",
                ],
                "storage": "inline",
                "source": metrics_csv.getvalue().decode("utf-8"),
            },
        ],
    }

    for cid, confusion_matrix in strategy.confusion_matrices[-1].items():
        # Convert to format expected by Kubeflow
        cm_data = []
        for i, col in enumerate(confusion_matrix.iteritems()):
            for j, row in enumerate(col[1].iteritems()):
                if j > i:
                    break
                cm_data.append((col[0], row[0], row[1]))

        df_cm = pd.DataFrame(cm_data, columns=["target", "predicted", "count"])

        confusion_csv = io.BytesIO()
        df_cm.to_csv(confusion_csv, header=False, index=False)

        metadata["outputs"].append(
            {
                "type": "confusion_matrix",
                "format": "csv",
                "schema": [
                    {"name": "target", "type": "CATEGORY"},
                    {"name": "predicted", "type": "CATEGORY"},
                    {"name": "count", "type": "NUMBER"},
                ],
                "labels": confusion_matrix.columns.tolist(),
                "storage": "inline",
                "source": confusion_csv.getvalue().decode("utf-8"),
            }
        )

    Path(args.metadata_output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(args.metadata_output_path).write_text(json.dumps(metadata))
