import concurrent.futures as futures
import io
import logging
from typing import List, Optional, Tuple

import numpy as np
from correlation import AggregationData, distributed_correlation
from flwr.common import Disconnect, PropertiesIns, PropertiesRes, Reconnect, Scalar
from flwr.server.client_manager import ClientManager
from flwr.server.client_proxy import ClientProxy
from flwr.server.history import History


class CorrelationServer:
    def __init__(self, client_manager: ClientManager, min_available_clients: int) -> None:
        self._client_manager = client_manager
        self._min_available_clients = min_available_clients

    def client_manager(self) -> ClientManager:
        return self._client_manager

    def fit(self, num_rounds: int, timeout: Optional[float]) -> History:
        history = History()

        print(f"waiting for {self._min_available_clients} to connect")

        # TODO: actually allow to configure the connection timeout here.
        self._client_manager.wait_for(self._min_available_clients, 86400)

        print("clients connected, starting correlation")

        with futures.ThreadPoolExecutor() as executor:
            submitted_fs = {
                executor.submit(
                    get_client_properties, client_proxy, PropertiesIns({}), timeout
                )
                for client_proxy in self._client_manager.all().values()
            }
            finished_fs, _ = futures.wait(fs=submitted_fs, timeout=None)

        client_data: List[AggregationData] = []

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

                num_features = properties["features"]
                client_data.append(
                    AggregationData(
                        num_entries=properties["entries"],
                        sums=scalar_to_numpy(properties["sums"]),
                        multiply_sums=scalar_to_numpy(properties["multiply_sums"]),
                        variances=scalar_to_numpy(properties["variances"]),
                    )
                )

        self.correlation = distributed_correlation(
            num_features=num_features, data=client_data
        )

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
