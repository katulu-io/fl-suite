import argparse
import logging
from pathlib import Path
from typing import Dict

import flwr
from flwr.server.client_manager import SimpleClientManager

from .correlation import CorrelationProvider
from .fedhist import HistogramProvider
from .provider import AnalyticsProvider
from .server import AnalyticsServer

log = logging.getLogger(__name__)

if __name__ == "__main__":
    providers: Dict[str, AnalyticsProvider] = {
        "correlation": CorrelationProvider(),
        "histogram": HistogramProvider(),
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--min-available-clients",
        type=int,
        default=2,
        help="Minimal number of clients to participate in federated learning",
    )
    parser.add_argument(
        "--metadata-output-path",
        type=str,
        help="Path to the file containing JSON metadata",
    )

    subparsers = parser.add_subparsers(dest="provider", required=True)

    for name, provider in providers.items():
        provider_parser = subparsers.add_parser(name)
        provider.add_arguments(provider_parser)

    args = parser.parse_args()

    log.info(f"using {args.provider}")

    provider = providers.get(args.provider)
    if provider is None:
        raise Exception(f"Unknown provider {args.provider}")

    provider.set_arguments(args)

    client_manager = SimpleClientManager()

    server = AnalyticsServer(
        client_manager=client_manager,
        min_available_clients=args.min_available_clients,
        provider=provider,
    )

    flwr.server.start_server(server=server, config={"num_rounds": 1})

    log.info(f"{provider.name} completed, preparing output")
    metadata = provider.result_metadata_json()

    # The output paths might not exist yet.
    # In that case create it.
    Path(args.metadata_output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(args.metadata_output_path).write_text(metadata)
