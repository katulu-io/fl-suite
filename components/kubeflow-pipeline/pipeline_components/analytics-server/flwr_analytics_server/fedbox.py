import io
import json
from typing import Any, Dict, cast

import matplotlib.pyplot as plt

from flwr_analytics_server.fedhist import (
    HistogramProvider,
    aggregate_histograms,
)
from flwr_analytics_server.fivenum import FiveNum, compute_fivesum


class BoxPlotProvider(HistogramProvider):
    def aggregate(self) -> None:
        histogram_data = aggregate_histograms(self._client_data)
        client_input = self.client_input_data()
        self._fivesum = compute_fivesum(
            float(client_input["hmin"]),
            float(client_input["hmax"]),
            histogram_data,
        )

    def result_metadata_json(self) -> str:

        five_num_info: Dict[str, Any] = {}
        five_num_info["label"] = "box"  # not required
        five_num_info["med"] = self._fivesum.median
        five_num_info["q1"] = self._fivesum.quartile_first
        five_num_info["q3"] = self._fivesum.quartile_third
        five_num_info["whislo"] = self._fivesum.maximum
        five_num_info["whishi"] = self._fivesum.minimum
        five_num_info["fliers"] = []

        stats = [five_num_info]

        fig_svg = io.BytesIO()

        fig, axes = plt.subplots(1, 1)
        axes.bxp(stats)
        axes.set_title("Box plot out of fiveNumSummary ")
        axes.set_ylabel("Values")
        plt.savefig(
            fig_svg,
            facecolor="w",
            edgecolor="w",
            transparent=False,
            format="svg",
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
