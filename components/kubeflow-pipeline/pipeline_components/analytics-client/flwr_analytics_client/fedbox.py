from flwr_analytics_client.fedhist import HistogramProvider


class BoxPlotProvider(HistogramProvider):
    @property
    def name(self) -> str:
        return "boxplot"
