"""

Federated Histogram Utilities : Functional tests

Katulu GmbH 
(c) 2022 

"""
import io

import numpy as np
from flwr.common import Scalar

from flwr_analytics_server.fedhist import HistogramProvider

def _numpy_to_scalar(input: np.ndarray) -> Scalar:
    buf = io.BytesIO()
    np.save(buf, input)

    return buf.getvalue()


def run_two_client_example(_rtol=1e-05, _atol=1e-08) -> None:
    """Run two client histogram construction."""
    #
    # Two client : histogram constuction
    #
    # Test data
    #
    np.random.seed(4242)
    global_data = np.random.gamma(shape=2.0, scale=2.0, size=1000)
    local_data_0 = global_data[0:500]
    local_data_1 = global_data[500:1000]
    #
    # Compute local histograms
    #
    client_0_histogram = np.histogram(local_data_0, bins=90, range=(0.14, 23.0))
    client_1_histogram = np.histogram(local_data_1, bins=90, range=(0.14, 23.0))
    #
    # Aggregation for global histogram
    #
    provider = HistogramProvider()
    provider.add_client_data({
        "counts": _numpy_to_scalar(client_0_histogram[0]),
        "bins": _numpy_to_scalar(client_0_histogram[1]),
        })
    provider.add_client_data({
        "counts": _numpy_to_scalar(client_1_histogram[0]),
        "bins": _numpy_to_scalar(client_1_histogram[1]),
        })

    provider.aggregate()
    global_histogram = provider._result
    #
    # Global data histogram
    #
    _counts, _bins = np.histogram(global_data, bins=90, range=(0.14, 23.0))
    #
    # Assertions
    #
    assert np.allclose(_counts, global_histogram.counts, atol=_atol, rtol=_rtol)
    assert np.allclose(_bins, global_histogram.bins)


def test_two_clients_gamma() -> None:
    """Two client example."""
    run_two_client_example()
