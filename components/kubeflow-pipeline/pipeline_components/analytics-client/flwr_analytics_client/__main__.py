import logging
from typing import List

import flwr

from .client import AnalyticsClient
from .correlation import CorrelationProvider
from .data import data
from .fedhist import HistogramProvider
from .provider import AnalyticsProvider

log = logging.getLogger(__name__)

if __name__ == "__main__":
    d = data()

    providers: List[AnalyticsProvider] = [
        CorrelationProvider(d),
        HistogramProvider(d),
    ]

    log.info(f"starting client with {', '.join(p.name for p in providers) } providers")

    client = AnalyticsClient(providers=providers)
    flwr.client.start_client(server_address="localhost:9080", client=client)
