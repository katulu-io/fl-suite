import numpy as np
from diffprivlib.tools import histogram as histogram_dp
from flwr.common import Config, Properties

from .provider import AnalyticsProvider, numpy_to_scalar


class HistogramProvider(AnalyticsProvider):
    def __init__(self, data: np.ndarray) -> None:
        self._data = data

    @property
    def name(self) -> str:
        return "histogram"

    def get_properties(self, config: Config) -> Properties:
        nbins = config["nbins"]
        hrange = (config["hmin"], config["hmax"])

        epsilon = config.get("epsilon")
        if epsilon is not None:
            counts, bins = histogram_dp(
                self._data,
                bins=nbins,
                range=hrange,
                epsilon=epsilon,
            )
        else:
            counts, bins = np.histogram(
                self._data,
                bins=nbins,
                range=hrange,
            )

        return {
            "counts": numpy_to_scalar(counts),
            "bins": numpy_to_scalar(bins),
        }
