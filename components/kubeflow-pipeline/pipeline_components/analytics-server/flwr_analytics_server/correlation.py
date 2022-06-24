import io
import json
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
from flwr.common import Properties, Scalar

from .provider import AnalyticsProvider, scalar_to_numpy


@dataclass
class AggregationData:
    num_features: int
    num_entries: int
    sums: np.ndarray
    multiply_sums: np.ndarray
    variances: np.ndarray


class CorrelationProvider(AnalyticsProvider):
    def __init__(self) -> None:
        self._client_data: List[AggregationData] = []

    def client_input_data(self) -> Dict[str, Scalar]:
        return {}

    def add_client_data(self, properties: Properties) -> None:
        self._client_data.append(
            AggregationData(
                num_features=properties["features"],
                num_entries=properties["entries"],
                sums=scalar_to_numpy(properties["sums"]),
                multiply_sums=scalar_to_numpy(properties["multiply_sums"]),
                variances=scalar_to_numpy(properties["variances"]),
            )
        )

    def aggregate(self) -> None:
        num_features = self._client_data[0].num_features
        self._result = distributed_correlation(num_features, self._client_data)

    def result_metadata_json(self) -> str:
        fig_svg = io.BytesIO()

        fig, ax = plt.subplots()
        ax.matshow(self._result)

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

        return json.dumps(metadata)

    def add_arguments(self, parser: ArgumentParser) -> None:
        pass

    def set_arguments(self, args: Namespace) -> None:
        pass

    @property
    def name(self) -> str:
        return "correlation"


def distributed_correlation(
    num_features: int, data: List[AggregationData]
) -> np.ndarray:
    total_entries = np.sum([d.num_entries for d in data])
    total_sums = np.sum([d.sums for d in data], axis=0)
    total_multiply_sums = np.sum([d.multiply_sums for d in data], axis=0)

    variances = _calc_variances(num_features, total_entries, total_sums, data)
    covariances = _calc_covariances(
        num_features, total_entries, total_sums, total_multiply_sums
    )

    corr_coeffs = np.zeros((num_features, num_features))
    for i in range(num_features):
        for j in range(num_features):
            corr_coeffs[i, j] = covariances[i, j] / (
                np.sqrt(variances[i]) * np.sqrt(variances[j])
            )

    return corr_coeffs


def _calc_variances(
    num_features: int,
    total_entries: int,
    total_sums: np.ndarray,
    data: List[AggregationData],
) -> np.ndarray:
    variances = np.zeros(num_features)

    total_avg = total_sums / total_entries

    variances = np.zeros(num_features)
    for i in range(num_features):
        numerator = 0
        for client in data:
            client_avg = client.sums[i] / client.num_entries
            variance_contribution = client.num_entries * (
                client.variances[i] + np.power(client_avg - total_avg[i], 2)
            )
            numerator += variance_contribution
        variances[i] = numerator / total_entries

    return variances


def _calc_covariances(
    num_features: int,
    total_entries: int,
    total_sums: np.ndarray,
    total_multiply_sums: np.ndarray,
) -> np.ndarray:
    covariances = np.zeros((num_features, num_features))
    for i in range(num_features):
        for j in range(num_features):
            avg_i = total_sums[i] / total_entries
            avg_j = total_sums[j] / total_entries
            avg_multiply = total_multiply_sums[i, j] / total_entries
            covariances[i, j] = avg_multiply - (avg_i * avg_j)

    return covariances
