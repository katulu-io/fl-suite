import io

import numpy as np
from flwr.common import Scalar

from flwr_analytics_client.correlation import CorrelationProvider


def _scalar_to_numpy(scalar: Scalar) -> np.ndarray:
    buf = io.BytesIO(scalar)
    return np.load(buf)


def test_correlation() -> None:
    test_data = np.array(
        [
            [1, 2, 4, 3, 0, 3, 95, 252],
            [3, 1, 1, 3, 23, 3, 9, 211],
            [3, 5, 8, 3, 1, 12, 19, 654],
        ]
    )

    provider = CorrelationProvider(test_data)

    properties = provider.get_properties({})

    features = properties["features"]
    np.testing.assert_equal(features, 8)
    entries = properties["entries"]
    np.testing.assert_equal(entries, 3)
    sums = _scalar_to_numpy(properties["sums"])
    np.testing.assert_equal(sums, [7, 8, 13, 9, 24, 18, 123, 1117])
    multiply_sums = _scalar_to_numpy(properties["multiply_sums"])
    np.testing.assert_almost_equal(
        multiply_sums,
        [
            [19, 20, 31, 21, 72, 48, 179, 2847],
            [20, 30, 49, 24, 28, 69, 294, 3985],
            [31, 49, 81, 39, 31, 111, 541, 6451],
            [21, 24, 39, 27, 72, 54, 369, 3351],
            [72, 28, 31, 72, 530, 81, 226, 5507],
            [48, 69, 111, 54, 81, 162, 540, 9237],
            [179, 294, 541, 369, 226, 540, 9467, 38265],
            [2847, 3985, 6451, 3351, 5507, 9237, 38265, 535741],
        ],
    )
    variances = _scalar_to_numpy(properties["variances"])
    np.testing.assert_almost_equal(
        variances,
        [
            8.888889e-01,
            2.888889e00,
            8.222222e00,
            0.000000e00,
            1.126667e02,
            1.800000e01,
            1.474667e03,
            3.994822e04,
        ],
        decimal=2,
    )
