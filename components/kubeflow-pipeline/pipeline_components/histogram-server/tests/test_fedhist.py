"""

Federated Histogram Utilities : Functional tests

Katulu GmbH 
(c) 2022 

"""
import numpy as np
from fedhist import Histogram, HistogramData, HistogramGlobal


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
    # Global & local objects
    #
    global_histogram = HistogramGlobal(
        histogram=Histogram(hrange=[0.14, 23.0], nbins=90)
    )
    client_0 = HistogramData(
        data_vector=local_data_0,
        histogram=Histogram(hrange=[0.14, 23.0], nbins=90),
    )
    client_1 = HistogramData(
        data_vector=local_data_1,
        histogram=Histogram(hrange=[0.14, 23.0], nbins=90),
    )
    #
    # Compute local histograms
    #
    client_0.compute_histogram()
    client_1.compute_histogram()
    #
    # Aggregation for global histogram
    #
    local_histograms = [client_0.histogram, client_1.histogram]
    global_histogram.local_histograms = local_histograms
    global_histogram.aggregate_histograms()
    #
    # Global data histogram
    #
    _counts, _bins = np.histogram(global_data, bins=90, range=[0.14, 23.0])
    #
    # Assertions
    #
    assert np.allclose(
        _counts, global_histogram.histogram.counts, atol=_atol, rtol=_rtol
    )
    assert np.allclose(_bins, global_histogram.histogram.bins)


def test_two_clients_gamma() -> None:
    """Two client example."""
    run_two_client_example()
