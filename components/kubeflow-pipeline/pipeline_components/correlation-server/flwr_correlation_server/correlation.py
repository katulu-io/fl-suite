from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class AggregationData:
    num_entries: int
    sums: np.ndarray
    multiply_sums: np.ndarray
    variances: np.ndarray


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
