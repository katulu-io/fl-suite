import io
import json
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Any, Dict, List, cast

import matplotlib.pyplot as plt
import numpy as np
from flwr.common import Properties, Scalar
from numpy.typing import NDArray

from flwr_analytics_server.provider import AnalyticsProvider, bytes_to_numpy


@dataclass
class HistogramData:
    counts: NDArray[Any]
    bins: NDArray[Any]


class HistogramProvider(AnalyticsProvider):
    def __init__(self) -> None:
        self._client_data: List[HistogramData] = []
        self.nbins = 0
        self.hrange = (0.0, 0.0)

    def client_input_data(self) -> Dict[str, Scalar]:
        return {
            "nbins": self.nbins,
            "hmin": self.hrange[0],
            "hmax": self.hrange[1],
        }

    def add_client_data(self, properties: Properties) -> None:
        self._client_data.append(
            HistogramData(
                counts=bytes_to_numpy(cast(bytes, properties["counts"])),
                bins=bytes_to_numpy(cast(bytes, properties["bins"])),
            )
        )

    def aggregate(self) -> None:
        self._result = aggregate_histograms(self._client_data)

    def result_metadata_json(self) -> str:
        fig_svg = io.BytesIO()

        fix, ax = plt.subplots()

        ax.hist(
            self._result.bins[:-1],
            self._result.bins,
            weights=self._result.counts,
        )

        plt.savefig(fig_svg, format="svg")

        metadata = {
            "version": 1,
            "outputs": [
                {
                    "type": "web-app",
                    "storage": "inline",
                    "source": fig_svg.getvalue().decode("utf-8"),
                },
            ],
        }

        return json.dumps(metadata)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--nbins",
            type=int,
            required=True,
        )
        parser.add_argument(
            "--hmin",
            type=float,
            required=True,
        )
        parser.add_argument(
            "--hmax",
            type=float,
            required=True,
        )

    def set_arguments(self, args: Namespace) -> None:
        self.nbins = args.nbins
        self.hrange = (args.hmin, args.hmax)

    @property
    def name(self) -> str:
        return "histogram"


def aggregate_histograms(histograms: List[HistogramData]) -> HistogramData:
    bins = histograms[0].bins
    counts = np.sum([h.counts for h in histograms], axis=0)

    return HistogramData(
        counts=counts,
        bins=bins,
    )
