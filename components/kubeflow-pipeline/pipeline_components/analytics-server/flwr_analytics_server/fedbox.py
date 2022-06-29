import io
import json
from argparse import ArgumentParser, Namespace
from typing import Dict, List, Tuple
from .fivenum import compute_fivesum, FiveNum
from .fedhist import aggregate_histograms, HistogramProvider, HistogramData
import matplotlib.pyplot as plt
import numpy as np
from flwr.common import Properties, Scalar
from .provider import AnalyticsProvider, scalar_to_numpy


class BoxPlotProvider(HistogramProvider):

    def aggregate(self) -> None:

        super().aggregate()
        histogram = self._result
        client_input = self.client_input_data()
        self._result = compute_fivesum(client_input['hmin'], client_input['hmax'], histogram)

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

    @property
    def name(self) -> str:
        return "boxplot"
