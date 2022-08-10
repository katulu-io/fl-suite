from datetime import datetime

import grpc
from flask import current_app, request
from kubeflow.kubeflow.crud_backend import (api, decorators, helpers, logging,
                                            status)
from spire.api.server.agent.v1 import agent_pb2, agent_pb2_grpc
from spire.api.server.entry.v1 import entry_pb2, entry_pb2_grpc
from spire.api.types import entry_pb2 as entry_type
from spire.api.types import selector_pb2, spiffeid_pb2

from ..db import get_db, query_db
from . import bp

log = logging.getLogger(__name__)


@bp.route("/api/namespaces/<namespace>/edges", methods=["POST"])
@decorators.request_is_json_type
@decorators.required_body_params("name")
def post_edge(namespace):
    body = request.get_json()
    log.info("Received body: %s", body)

    # TODO: Refactor into model
    edge_name = body["name"]
    created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    spire_config = current_app.config["FL_SUITE_CONFIG"]["fl_edge"]["auth"]["spire"]
    join_token = register_spire_workloads(
        spire_config["trust_domain"],
        edge_name,
    )

    db_connection = get_db()
    cur = db_connection.cursor()
    insert_edge_sql = "INSERT INTO Edge(name, namespace, created_at) VALUES(?, ?, ?)"
    cur.execute(insert_edge_sql, (edge_name, namespace, created_at))

    results = query_db(
        "select edge_id from Edge where name = ? and namespace = ?",
        (edge_name, namespace),
    )
    if results is None:
        return api.failed_response("Unexpected error", 500)

    new_edge_id = results[0]["edge_id"]

    insert_join_token_auth_sql = (
        "INSERT INTO JoinTokenAuth(edge_id, join_token) VALUES(?, ?)"
    )
    cur.execute(insert_join_token_auth_sql, (new_edge_id, join_token))
    db_connection.commit()

    fl_operator_config = current_app.config["FL_SUITE_CONFIG"]["fl_operator"]
    # TODO: Refactor into model
    new_edge = {
        "name": edge_name,
        "namespace": namespace,
        # The status is hardcoded because it is only used for presentation purposes
        "status": status.create_status(status.STATUS_PHASE.READY, "Ready"),
        "age": helpers.get_uptime(created_at),
        "join_token": join_token,
    }
    new_edge.update(spire_config)
    new_edge.update(fl_operator_config)

    log.info("Successfully created Edge %s/%s", namespace, edge_name)

    return api.success_response("edge", new_edge)


def register_spire_workloads(trust_domain: str, edge_name: str) -> str:
    # Hard-coded to use spire-server's unix socket only. Used to get admin access.
    with grpc.insecure_channel("unix:///tmp/spire-server/private/api.sock") as channel:
        stub = agent_pb2_grpc.AgentStub(channel)

        edge_spiffe_id = spiffeid_pb2.SPIFFEID(
            trust_domain=trust_domain, path=f"/{edge_name}"
        )
        join_token_request = agent_pb2.CreateJoinTokenRequest(
            ttl=600, agent_id=edge_spiffe_id
        )
        join_token = stub.CreateJoinToken(join_token_request)

        fl_operator_entry = entry_type.Entry(
            parent_id=edge_spiffe_id,
            spiffe_id=spiffeid_pb2.SPIFFEID(
                trust_domain=trust_domain, path="/fl-operator"
            ),
            selectors=[
                selector_pb2.Selector(
                    type="k8s", value="pod-label:app:fl-operator-envoyproxy"
                )
            ],
        )
        flower_client_entry = entry_type.Entry(
            parent_id=edge_spiffe_id,
            spiffe_id=spiffeid_pb2.SPIFFEID(
                trust_domain=trust_domain,
                path="/flower-client",
            ),
            selectors=[
                selector_pb2.Selector(type="k8s", value="pod-label:app:flower-client")
            ],
        )
        entry_stub = entry_pb2_grpc.EntryStub(channel)
        entry_batch_request = entry_pb2.BatchCreateEntryRequest(
            entries=[flower_client_entry, fl_operator_entry]
        )
        entry_stub.BatchCreateEntry(entry_batch_request)

        return join_token.value
