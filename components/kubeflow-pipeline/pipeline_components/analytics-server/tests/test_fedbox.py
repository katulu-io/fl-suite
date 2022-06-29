"""

Federated FedBox Utilities : Functional tests

Katulu GmbH 
(c) 2022 

"""
import io
import argparse
import numpy as np
from flwr.common import Scalar
from flwr_analytics_server.fedbox import BoxPlotProvider

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
    global_data = np.random.normal(size=1000, loc=20)
    local_data_0 = global_data[0:500]
    local_data_1 = global_data[500:1000]
    #
    # Compute local histograms
    #
    client_0_histogram = np.histogram(local_data_0, bins=100, range=(17.0, 24.0))
    client_1_histogram = np.histogram(local_data_1, bins=100, range=(17.0, 24.0))
    #
    # Aggregation for global histogram
    #
    provider = BoxPlotProvider()
    args = argparse.Namespace()
    args.nbins = 100
    args.hmin = 17.0
    args.hmax = 24.0
    provider.set_arguments(args)

    provider.add_client_data({
        "counts": _numpy_to_scalar(client_0_histogram[0]),
        "bins": _numpy_to_scalar(client_0_histogram[1]),
        })
    provider.add_client_data({
        "counts": _numpy_to_scalar(client_1_histogram[0]),
        "bins": _numpy_to_scalar(client_1_histogram[1]),
        })

    provider.aggregate()
    fivenum = provider._result
    _fivenum = [fivenum.minimum, fivenum.quartile_first, fivenum.median, fivenum.quartile_third, fivenum.maximum]
    _fivenum_precomputed = [17.0, 17.21, 17.91, 19.03, 24.0]
    #
    # Assertion
    #
    assert np.allclose(_fivenum, _fivenum_precomputed, atol=_atol, rtol=_rtol)


def test_two_clients_normal() -> None:
    """Two client example."""
    run_two_client_example()
