import io
from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from flwr.common import Config, Properties, Scalar
from numpy.typing import NDArray


class AnalyticsProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def get_properties(self, _: Config) -> Properties:
        pass


def numpy_to_scalar(input: NDArray[Any]) -> Scalar:
    buf = io.BytesIO()

    np.save(buf, input)

    return buf.getvalue()
