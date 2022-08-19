import logging
from typing import List

import flwr

from flwr_analytics_client.client import AnalyticsClient
from flwr_analytics_client.correlation import CorrelationProvider
from flwr_analytics_client.data import data
from flwr_analytics_client.fedbox import BoxPlotProvider
from flwr_analytics_client.fedhist import HistogramProvider
from flwr_analytics_client.provider import AnalyticsProvider

log = logging.getLogger(__name__)

if __name__ == "__main__":
    d = data()

    providers: List[AnalyticsProvider] = [
        CorrelationProvider(d),
        HistogramProvider(d),
        BoxPlotProvider(d),
    ]

    log.info(
        f"starting client with {', '.join(p.name for p in providers) } providers"
    )

    client = AnalyticsClient(providers=providers)
    flwr.client.start_client(server_address="localhost:9080", client=client)
