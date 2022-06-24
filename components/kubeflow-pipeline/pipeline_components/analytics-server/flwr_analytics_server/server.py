import concurrent.futures as futures
import logging
from typing import Optional, Tuple

from flwr.common import Disconnect, PropertiesIns, PropertiesRes, Reconnect
from flwr.server.client_manager import ClientManager
from flwr.server.client_proxy import ClientProxy
from flwr.server.history import History

from .provider import AnalyticsProvider

log = logging.getLogger(__name__)


class AnalyticsServer:
    def __init__(
        self,
        client_manager: ClientManager,
        min_available_clients: int,
        provider: AnalyticsProvider,
    ) -> None:
        self._client_manager = client_manager
        self._min_available_clients = min_available_clients
        self._provider = provider

    def client_manager(self) -> ClientManager:
        return self._client_manager

    def fit(self, num_rounds: int, timeout: Optional[float]) -> History:
        history = History()

        log.info(f"waiting for {self._min_available_clients} clients to connect")

        # TODO: actually allow to configure the connection timeout here.
        self._client_manager.wait_for(self._min_available_clients, 86400)

        log.info(f"clients connected, starting {self._provider.name}")

        ins = PropertiesIns(
            {
                "provider": self._provider.name,
                **self._provider.client_input_data(),
            }
        )

        with futures.ThreadPoolExecutor() as executor:
            submitted_fs = {
                executor.submit(get_client_properties, client_proxy, ins, timeout)
                for client_proxy in self._client_manager.all().values()
            }
            finished_fs, _ = futures.wait(fs=submitted_fs, timeout=None)

        for future in finished_fs:
            failure = future.exception()
            if failure is not None:
                log.warning(
                    f"Failed to retrieve client properties of a client: {failure}"
                )
                pass
            else:
                result = future.result()
                properties = result[1].properties

                self._provider.add_client_data(properties=properties)

        self._provider.aggregate()
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
