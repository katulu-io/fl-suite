from io import BytesIO
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from flwr.common import EvaluateRes, FitRes, Parameters, Scalar, parameters_to_weights
from flwr.server.client_proxy import ClientProxy
from flwr.server.strategy import FedAvg


class FedAvgStoreModelStrategy(FedAvg):
    def __init__(self, local_epochs: int = 1, **kwargs) -> None:
        def fit_config(round):
            return {"epochs": str(local_epochs)}

        super().__init__(on_fit_config_fn=fit_config, **kwargs)

        self.metrics: List[Dict[str, Dict[str, float]]] = []
        self.confusion_matrices: List[Dict[str, np.ndarray]] = []
        self.weights: List[np.ndarray] = []
        self.correlations: Dict[str, pd.DataFrame] = {}  # HACK

    def aggregate_fit(
        self,
        round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[BaseException],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        parameters, config = super().aggregate_fit(round, results, failures)
        if parameters is not None:
            aggregated_weights = parameters_to_weights(parameters)
            self.weights.append(aggregated_weights)

        return parameters, config

    def aggregate_evaluate(
        self,
        rnd: int,
        results: List[Tuple[ClientProxy, EvaluateRes]],
        failures: List[BaseException],
    ) -> Tuple[Optional[float], Dict[str, Scalar]]:
        metrics = {}
        confmats = {}
        correlations = {}

        for client, result in results:
            if client.cid not in metrics:
                metrics[client.cid] = {}

            if "accuracy" in result.metrics:
                metrics[client.cid]["accuracy"] = result.metrics["accuracy"]

            if "precision" in result.metrics:
                metrics[client.cid]["precision"] = result.metrics["precision"]

            if "recall" in result.metrics:
                metrics[client.cid]["recall"] = result.metrics["recall"]

            if "confusion_matrix" in result.metrics:
                bytes_io = BytesIO(result.metrics["confusion_matrix"])
                confmat = np.load(bytes_io, allow_pickle=False)
                confmats[client.cid] = confmat

            if "correlation_matrix" in result.metrics:
                bytes_io = BytesIO(result.metrics["correlation_matrix"])
                correlations[client.cid] = pd.read_pickle(bytes_io)

            metrics[client.cid]["examples"] = result.num_examples

        self.metrics.append(metrics)
        self.confusion_matrices.append(confmats)
        self.correlations = correlations

        return super().aggregate_evaluate(rnd, results, failures)
