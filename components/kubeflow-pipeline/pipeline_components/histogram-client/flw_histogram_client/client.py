import io

import numpy as np
from flwr.client import Client
from flwr.common import (
    Code,
    EvaluateIns,
    EvaluateRes,
    FitIns,
    FitRes,
    ParametersRes,
    PropertiesIns,
    PropertiesRes,
    Scalar,
    Status,
)

import data
from fedhist import Histogram, HistogramData, HistogramGlobal


class HistogramClient(Client):
    def __init__(self, data_id: int) -> None:
        self.data_id = data_id

    def get_properties(self, properties_in: PropertiesIns) -> PropertiesRes:
        data_vector = data.data(self.data_id)
        histogram_config = properties_in.config
        print("Global histogram configuration :", histogram_config)

        nbins = histogram_config["nbins"]
        hmin = histogram_config["hmin"]
        hmax = histogram_config["hmax"]

        client_histogram = Histogram(nbins=nbins, hrange=[hmin, hmax])
        client_histogram_data = HistogramData(
            data_vector=data_vector, histogram=client_histogram
        )
        client_histogram_data.compute_histogram()
        res = PropertiesRes(
            status=Status(Code.OK, "OK"),
            properties={
                "counts": numpy_to_scalar(client_histogram_data.histogram.counts),
                "bins": numpy_to_scalar(client_histogram_data.histogram.bins),
            },
        )

        return res

    def get_parameters(self) -> ParametersRes:
        return ParametersRes()

    def fit(self, ins: FitIns) -> FitRes:
        return FitRes()

    def evaluate(self, ins: EvaluateIns) -> EvaluateRes:
        return EvaluateRes()


def numpy_to_scalar(input: np.ndarray) -> Scalar:
    buf = io.BytesIO()
    np.save(buf, input)
    return buf.getvalue()
