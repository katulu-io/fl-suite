""" 

Five number summary given histogram.   
Bases for a Boxplot.  

Katulu GmbH  
(c) 2022  

"""

from dataclasses import dataclass
from typing import List, Optional, cast

import numpy as np

from flwr_analytics_server.fedhist import HistogramData


@dataclass
class FiveNum:
    """Five numbers for box plot."""

    minimum: float
    quartile_first: float
    median: float
    quartile_third: float
    maximum: float


def compute_fivesum(
    hmin: float, hmax: float, histogram: HistogramData
) -> FiveNum:
    """Compute five number summary."""

    def inverse_value_bin(histogram: HistogramData, yvalue: float) -> float:
        """

        Return closest bin edge given yvalue : count

        """
        idx = (np.abs(yvalue - histogram.counts)).argmin()
        return float(histogram.bins[idx])

    dist = histogram.counts

    fivenum = FiveNum(
        minimum=hmin,
        quartile_first=inverse_value_bin(histogram, np.quantile(dist, q=0.25)),
        median=inverse_value_bin(histogram, np.quantile(dist, q=0.50)),
        quartile_third=inverse_value_bin(histogram, np.quantile(dist, q=0.75)),
        maximum=hmax,
    )
    return fivenum
