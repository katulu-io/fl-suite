"""

Federated Histogram Flower Server

Katulu GmbH  
(c) 2022  

"""
import concurrent.futures as futures
import io
import logging
from typing import List, Optional, Tuple

import numpy as np
from flwr.common import Disconnect, PropertiesIns, PropertiesRes, Reconnect, Scalar
from flwr.server.client_manager import ClientManager
from flwr.server.client_proxy import ClientProxy
from flwr.server.history import History

from fedhist import Histogram, LocalHistograms, HistogramData, HistogramGlobal


class HistogramServer:
    def __init__(
        self,
        client_manager: ClientManager,
        min_available_clients: int,
        nbins: int,
        hmin: float,
        hmax: float,
    ) -> None:
        self._client_manager = client_manager
        self._min_available_clients = min_available_clients
        self.nbins = nbins
        self.hmin = hmin
        self.hmax = hmax
        self.histogram: Optional[HistogramGlobal] = None

    def client_manager(self) -> ClientManager:
        return self._client_manager

    def fit(self, num_rounds: int, timeout: Optional[float]) -> History:
        history = History()

        print(f"waiting for {self._min_available_clients} to connect")

        # TODO: actually allow to configure the connection timeout here.
        self._client_manager.wait_for(self._min_available_clients, 86400)

        print("FedHist : building aggregated histogram.")

        histogram_config = {"nbins": self.nbins, "hmin": self.hmin, "hmax": self.hmax}

        with futures.ThreadPoolExecutor() as executor:
            submitted_fs = {
                executor.submit(
                    get_client_properties,
                    client_proxy,
                    PropertiesIns(histogram_config),
                    timeout,
                )
                for client_proxy in self._client_manager.all().values()
            }
            finished_fs, _ = futures.wait(fs=submitted_fs, timeout=None)

        local_histograms: LocalHistograms = []

        for future in finished_fs:
            failure = future.exception()
            if failure is not None:
                logging.warning(
                    f"Failed to retrieve client properties of a client: {failure}"
                )
                pass
            else:
                result = future.result()
                properties = result[1].properties
                local_histograms.append(
                    Histogram(
                        nbins=self.nbins,
                        hrange=[self.hmin, self.hmax],
                        counts=scalar_to_numpy(properties["counts"]),
                        bins=scalar_to_numpy(properties["bins"]),
                    )
                )

        global_histogram = HistogramGlobal(
            histogram=Histogram(nbins=self.nbins, hrange=[self.hmin, self.hmax]),
            local_histograms=local_histograms,
        )

        global_histogram.aggregate_histograms()
        self.histogram = global_histogram

        print("FedHist : Completed. ")

        return history

    def disconnect_all_clients(self, timeout: Optional[float]) -> None:
        clients = self._client_manager.all().values()
        instruction = Reconnect(seconds=None)
        client_instructions = [(client_proxy, instruction) for client_proxy in clients]

        with futures.ThreadPoolExecutor() as executor:
            submitted_fs = {
                executor.submit(reconnect_client, client_proxy, ins, timeout)
                for client_proxy, ins in client_instructions
            }
            _, _ = futures.wait(fs=submitted_fs, timeout=None)


def scalar_to_numpy(scalar: Scalar) -> np.ndarray:
    buf = io.BytesIO(scalar)
    return np.load(buf)


def get_client_properties(
    client: ClientProxy, ins: PropertiesIns, timeout: Optional[float]
) -> Tuple[ClientProxy, PropertiesRes]:
    res = client.get_properties(ins, timeout=timeout)
    return client, res


def reconnect_client(
    client: ClientProxy, reconnect: Reconnect, timeout: Optional[float]
) -> Tuple[ClientProxy, Disconnect]:
    disconnect = client.reconnect(reconnect, timeout=timeout)
    return client, disconnect
