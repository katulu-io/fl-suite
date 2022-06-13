"""

Federated Histogram with differential privacy  

Katulu GmbH  
(c) 2022  

"""
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict
from diffprivlib.tools import histogram as histogram_dp

Vector = np.array


@dataclass
class Histogram:
    """Histogram information without the data."""

    nbins: int
    hrange: List
    counts: Optional[np.array] = None
    bins: Optional[np.array] = None


LocalHistograms = List[Histogram]


@dataclass
class HistogramData:
    """Local histogram data, compute with differential privacy support."""

    data_vector: Vector
    histogram: Histogram
    diffpriv: bool = False
    epsilon: float = 1.0

    def compute_histogram(self) -> None:
        """Populate counts bins."""
        if self.diffpriv is False:
            self.histogram.counts, self.histogram.bins = np.histogram(
                self.data_vector, bins=self.histogram.nbins, range=self.histogram.hrange
            )
        elif self.diffpriv is True:
            self.histogram.counts, self.histogram.bins = histogram_dp(
                self.data_vector,
                bins=self.histogram.nbins,
                range=self.histogram.hrange,
                epsilon=self.epsilon,
            )
        return None


@dataclass
class HistogramGlobal:
    """Server histogram."""

    histogram: Histogram
    local_histograms: Optional[LocalHistograms] = None

    def _assign_bins(self, local_index: int = 0) -> None:
        """Assign bins using local histograms."""
        self.histogram.bins = self.local_histograms[local_index].bins

    def aggregate_histograms(self) -> None:
        """Aggregate count and assign bins."""
        self.histogram.counts = np.zeros(self.histogram.nbins)
        current_number_of_clients = len(self.local_histograms)
        for _client_index in range(current_number_of_clients):
            self.histogram.counts += self.local_histograms[_client_index].counts
        self._assign_bins()
        return None
