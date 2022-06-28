import io
import json
from argparse import ArgumentParser, Namespace
from typing import Dict, List, Tuple
from .fivenum import compute_fivesum, FiveNum
from .fedhist import aggregate_histograms, HistogramData
import matplotlib.pyplot as plt
import numpy as np
from flwr.common import Properties, Scalar
from .provider import AnalyticsProvider, scalar_to_numpy


class BoxPlotProvider(AnalyticsProvider):
    def __init__(self) -> None:
        self._client_data: List[HistogramData] = []
        self.nbins = 0
        self.hrange = (0, 0)

    def client_input_data(self) -> Dict[str, Scalar]:
        return {
            "nbins": self.nbins,
            "hmin": self.hrange[0],
            "hmax": self.hrange[1],
        }

    def add_client_data(self, properties: Properties) -> None:
        self._client_data.append(
            HistogramData(
                counts=scalar_to_numpy(properties["counts"]),
                bins=scalar_to_numpy(properties["bins"]),
            )
        )

    def aggregate(self) -> None:
        client_input = self.client_input_data()
        hmin = client_input['hmin']
        hmax = client_input['hmax']
        histogram=aggregate_histograms(self._client_data)
        fn = compute_fivesum(hmin, hmax, histogram)
        self._result = fn

    def result_metadata_json(self) -> str:

        five_num_info = {}
        five_num_info["label"] = "box"  # not required
        five_num_info["med"] = self._result.median
        five_num_info["q1"] = self._result.quartile_first
        five_num_info["q3"] = self._result.quartile_third
        five_num_info["whislo"] = self._result.maximum
        five_num_info["whishi"] = self._result.minimum
        five_num_info["fliers"] = []

        stats = [five_num_info]

        fig_svg = io.BytesIO()

        fig, axes = plt.subplots(1, 1)
        axes.bxp(stats)
        axes.set_title("Box plot out of fiveNumSummary ")
        axes.set_ylabel("Values")
        plt.savefig(
            fig_svg, facecolor="w", edgecolor="w", transparent=False, format="svg"
        )

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
        return "boxplot"
