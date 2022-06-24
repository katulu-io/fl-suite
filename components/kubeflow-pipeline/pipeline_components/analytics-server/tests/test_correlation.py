import io

import numpy as np
from flwr.common import Scalar, Properties

from flwr_analytics_server.correlation import CorrelationProvider

def _numpy_to_scalar(input: np.ndarray) -> Scalar:
    buf = io.BytesIO()
    np.save(buf, input)

    return buf.getvalue()


def test_correlation() -> None:
    test_data = np.array(
        [
            [1, 2, 4, 3, 0, 3, 95, 252],
            [3, 1, 1, 3, 23, 3, 9, 211],
            [3, 5, 8, 3, 1, 12, 19, 654],
            [8, 6, 4, 7, 7, 65, 9, 245],
            [1, 2, 3, 5, 5, 3, 9, 342],
            [2, 5, 9, 3, 22, 76, 9, 1],
            [1, 26, 7, 3, 7, 24, 9, 323],
        ]
    )

    corr = np.corrcoef(test_data, rowvar=False)

    provider = CorrelationProvider()
    provider.add_client_data(_aggregate_data(test_data[0:3]))
    provider.add_client_data(_aggregate_data(test_data[3:5]))
    provider.add_client_data(_aggregate_data(test_data[5:7]))
    provider.aggregate()

    dist_corr = provider._result

    np.testing.assert_almost_equal(dist_corr, corr)


def _aggregate_data(data: np.ndarray) -> Properties:
    num_entries = data.shape[0]
    num_features = data.shape[1]

    multiply_sums = np.zeros((num_features, num_features))
    for i in range(0, num_entries):
        for j in range(0, num_features):
            for k in range(0, num_features):
                multiply_sums[j][k] += data[i][j] * data[i][k]

    return {
        "features": num_features,
        "entries": num_entries,
        "sums": _numpy_to_scalar(np.sum(data, axis=0)),
        "variances": _numpy_to_scalar(np.var(data, axis=0)),
        "multiply_sums": _numpy_to_scalar(multiply_sums),
    }
