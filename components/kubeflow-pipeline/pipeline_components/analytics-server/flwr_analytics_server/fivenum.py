""" 

Five number summary given histogram.   
Bases for a Boxplot.  

Katulu GmbH  
(c) 2022  

"""

import numpy as np
from dataclasses import dataclass
from typing import List, Optional
from .fedhist import HistogramData


@dataclass
class fiveNum:
    """Five numbers for box plot."""

    minimum: float
    quartile_first: float
    median: float
    quartile_third: float
    maximum: float


@dataclass
class fiveNumSummary:
    """Five number summary."""

    histogram: HistogramData
    hmin: float
    hmax: float
    fivenum: Optional[fiveNum] = None

    @staticmethod
    def inverse_value_bin(histogram: HistogramData, yvalue: float) -> float:
        """

        Return closest bin edge given yvalue : count

        """
        idx = (np.abs(yvalue - histogram.counts)).argmin()
        return histogram.bins[idx]

    def compute(self) -> None:
        """

        Compute fivenum.

        """
        dist = self.histogram.counts

        inverse_value_bin = self.inverse_value_bin

        histogram = self.histogram
        hmin = self.hmin
        hmax = self.hmax

        self.fivenum = fiveNum(
            minimum=hmin,
            quartile_first=inverse_value_bin(histogram, np.quantile(dist, q=0.25)),
            median=inverse_value_bin(histogram, np.quantile(dist, q=0.50)),
            quartile_third=inverse_value_bin(histogram, np.quantile(dist, q=0.75)),
            maximum=hmax,
        )
        return None
