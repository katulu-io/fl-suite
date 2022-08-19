from typing import Iterable

from flwr.client import Client
from flwr.common import (
    Code,
    EvaluateIns,
    EvaluateRes,
    FitIns,
    FitRes,
    GetParametersIns,
    GetParametersRes,
    GetPropertiesIns,
    GetPropertiesRes,
    Parameters,
    Status,
)

from flwr_analytics_client.provider import AnalyticsProvider


# TODO: remove 'type: ignore' once
# https://github.com/adap/flower/pull/1377 has been merged
class AnalyticsClient(Client):  # type: ignore
    def __init__(self, providers: Iterable[AnalyticsProvider]) -> None:
        self._providers = {p.name: p for p in providers}

    def get_properties(self, ins: GetPropertiesIns) -> GetPropertiesRes:
        provider_name = ins.config.get("provider")
        if provider_name is None:
            # TODO
            return GetPropertiesRes(
                status=Status(Code.GET_PARAMETERS_NOT_IMPLEMENTED, ""),
                properties={},
            )

        provider = self._providers.get(str(provider_name))
        if provider is None:
            # TODO
            return GetPropertiesRes(
                status=Status(Code.GET_PARAMETERS_NOT_IMPLEMENTED, ""),
                properties={},
            )

        properties = provider.get_properties(ins.config)

        res = GetPropertiesRes(
            status=Status(Code.OK, "OK"),
            properties=properties,
        )

        return res

    def get_parameters(self, ins: GetParametersIns) -> GetParametersRes:
        return GetParametersRes(
            status=Status(Code.OK, "OK"),
            parameters=Parameters(
                tensors=[],
                tensor_type="none",
            ),
        )

    def fit(self, ins: FitIns) -> FitRes:
        return FitRes(
            status=Status(Code.OK, "OK"),
            parameters=Parameters(
                tensors=[],
                tensor_type="none",
            ),
            num_examples=0,
            metrics={},
        )

    def evaluate(self, ins: EvaluateIns) -> EvaluateRes:
        return EvaluateRes(
            status=Status(Code.OK, "OK"),
            loss=0,
            num_examples=0,
            metrics={},
        )
