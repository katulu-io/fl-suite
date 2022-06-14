import io
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from typing import Dict

import numpy as np
from flwr.common import Properties, Scalar


class AnalyticsProvider(ABC):
    @abstractmethod
    def client_input_data(self) -> Dict[str, Scalar]:
        pass

    @abstractmethod
    def add_client_data(self, properties: Properties) -> None:
        pass

    @abstractmethod
    def aggregate(self) -> None:
        pass

    @abstractmethod
    def result_metadata_json(self) -> str:
        pass

    @abstractmethod
    def add_arguments(self, parser: ArgumentParser) -> None:
        pass

    @abstractmethod
    def set_arguments(self, args: Namespace) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


def scalar_to_numpy(scalar: Scalar) -> np.ndarray:
    buf = io.BytesIO(scalar)
    return np.load(buf)
