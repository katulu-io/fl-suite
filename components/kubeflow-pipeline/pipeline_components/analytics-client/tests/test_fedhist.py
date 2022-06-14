import io

import numpy as np
from flwr.common import Scalar

from flwr_analytics_client.fedhist import HistogramProvider


def _scalar_to_numpy(scalar: Scalar) -> np.ndarray:
    buf = io.BytesIO(scalar)
    return np.load(buf)


def test_histogram() -> None:
    data = np.array([0, 1, 0])

    provider = HistogramProvider(data)

    properties = provider.get_properties(
        {
            "nbins": 2,
            "hmin": 0,
            "hmax": 1,
        }
    )

    counts = _scalar_to_numpy(properties["counts"])
    np.testing.assert_equal(counts, [2, 1])
    bins = _scalar_to_numpy(properties["bins"])
    np.testing.assert_equal(bins, [0, 0.5, 1])
