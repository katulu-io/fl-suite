import numpy as np

from flwr_correlation_server.correlation import AggregationData, distributed_correlation


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

    data = [
        _aggregate_data(test_data[0:3]),
        _aggregate_data(test_data[3:5]),
        _aggregate_data(test_data[5:7]),
    ]

    dist_corr = distributed_correlation(8, data)

    np.testing.assert_almost_equal(dist_corr, corr)


def _aggregate_data(data: np.ndarray) -> AggregationData:
    num_entries = data.shape[0]
    num_features = data.shape[1]

    multiply_sums = np.zeros((num_features, num_features))
    for i in range(0, num_entries):
        for j in range(0, num_features):
            for k in range(0, num_features):
                multiply_sums[j][k] += data[i][j] * data[i][k]

    return AggregationData(
        num_entries=num_entries,
        sums=np.sum(data, axis=0),
        variances=np.var(data, axis=0),
        multiply_sums=multiply_sums,
    )
