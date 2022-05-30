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


class CorrelationClient(Client):
    def get_properties(self, _: PropertiesIns) -> PropertiesRes:
        d = data.data()

        entries = d.shape[0]
        features = d.shape[1]
        sums = np.sum(d, axis=0)
        variances = np.var(d, axis=0)
        multiply_sums = np.zeros((features, features))
        for i in range(0, entries):
            for j in range(0, features):
                for k in range(0, features):
                    multiply_sums[j][k] += d[i][j] * d[i][k]

        res = PropertiesRes(
            status=Status(Code.OK, "OK"),
            properties={
                "features": features,
                "entries": entries,
                "sums": numpy_to_scalar(sums),
                "multiply_sums": numpy_to_scalar(multiply_sums),
                "variances": numpy_to_scalar(variances),
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
