from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import numpy as np
import pandas as pd
from flwr.common import (
    EvaluateRes,
    FitRes,
    NDArrays,
    Parameters,
    Scalar,
    parameters_to_ndarrays,
)
from flwr.server.client_proxy import ClientProxy
from flwr.server.strategy import FedAvg
from numpy.typing import NDArray


# TODO: remove 'type: ignore' once
# https://github.com/adap/flower/pull/1377 has been merged
class FedAvgStoreModelStrategy(FedAvg):  # type: ignore
    def __init__(self, local_epochs: int = 1, **kwargs: Any) -> None:
        def fit_config(round: int) -> Dict[str, Scalar]:
            return {"epochs": str(local_epochs)}

        super().__init__(on_fit_config_fn=fit_config, **kwargs)

        self.metrics: List[Dict[str, Dict[str, Scalar]]] = []
        self.confusion_matrices: List[Dict[str, NDArray[Any]]] = []
        self.weights: List[NDArrays] = []
        self.correlations: Dict[str, pd.DataFrame] = {}  # HACK

    def aggregate_fit(
        self,
        round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        parameters, config = super().aggregate_fit(round, results, failures)
        if parameters is not None:
            aggregated_weights = parameters_to_ndarrays(parameters)
            self.weights.append(aggregated_weights)

        return parameters, config

    def aggregate_evaluate(
        self,
        rnd: int,
        results: List[Tuple[ClientProxy, EvaluateRes]],
        failures: List[Union[Tuple[ClientProxy, EvaluateRes], BaseException]],
    ) -> Tuple[Optional[float], Dict[str, Scalar]]:
        metrics: Dict[str, Dict[str, Scalar]] = {}
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
                bytes_io = BytesIO(
                    cast(bytes, result.metrics["confusion_matrix"])
                )
                confmat = np.load(bytes_io, allow_pickle=False)
                confmats[client.cid] = confmat

            if "correlation_matrix" in result.metrics:
                bytes_io = BytesIO(
                    cast(bytes, result.metrics["correlation_matrix"])
                )
                correlations[client.cid] = pd.read_pickle(bytes_io)

            metrics[client.cid]["examples"] = result.num_examples

        self.metrics.append(metrics)
        self.confusion_matrices.append(confmats)
        self.correlations = correlations

        # TODO: remove 'type: ignore' once
        # https://github.com/adap/flower/pull/1377 has been merged
        return super().aggregate_evaluate(rnd, results, failures)  # type: ignore
