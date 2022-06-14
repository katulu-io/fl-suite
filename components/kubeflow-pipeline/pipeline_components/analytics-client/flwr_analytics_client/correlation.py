import numpy as np
from flwr.common import Config, Properties

from .provider import AnalyticsProvider, numpy_to_scalar


class CorrelationProvider(AnalyticsProvider):
    def __init__(self, data: np.ndarray) -> None:
        self._data = data

    @property
    def name(self) -> str:
        return "correlation"

    def get_properties(self, _: Config) -> Properties:
        entries = self._data.shape[0]
        features = self._data.shape[1]
        sums = np.sum(self._data, axis=0)
        variances = np.var(self._data, axis=0)
        multiply_sums = np.zeros((features, features))
        for i in range(0, entries):
            for j in range(0, features):
                for k in range(0, features):
                    multiply_sums[j][k] += self._data[i][j] * self._data[i][k]

        return {
            "features": features,
            "entries": entries,
            "sums": numpy_to_scalar(sums),
            "multiply_sums": numpy_to_scalar(multiply_sums),
            "variances": numpy_to_scalar(variances),
        }
