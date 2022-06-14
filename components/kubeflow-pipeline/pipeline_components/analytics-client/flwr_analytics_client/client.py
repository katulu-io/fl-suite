from typing import List

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
    Status,
)

from .provider import AnalyticsProvider


class AnalyticsClient(Client):
    def __init__(self, providers: List[AnalyticsProvider]) -> None:
        self._providers = {p.name: p for p in providers}

    def get_properties(self, ins: PropertiesIns) -> PropertiesRes:
        provider_name = ins.config.get("provider")
        if provider_name is None:
            # TODO
            return PropertiesRes(
                status=Status(Code.GET_PARAMETERS_NOT_IMPLEMENTED, ""), properties={}
            )

        provider = self._providers.get(str(provider_name))
        if provider is None:
            # TODO
            return PropertiesRes(
                status=Status(Code.GET_PARAMETERS_NOT_IMPLEMENTED, ""), properties={}
            )

        properties = provider.get_properties(ins.config)

        res = PropertiesRes(
            status=Status(Code.OK, "OK"),
            properties=properties,
        )

        return res

    def get_parameters(self) -> ParametersRes:
        return ParametersRes()

    def fit(self, ins: FitIns) -> FitRes:
        return FitRes()

    def evaluate(self, ins: EvaluateIns) -> EvaluateRes:
        return EvaluateRes()
