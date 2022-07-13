from datetime import datetime

import grpc
from flask import request
from kubeflow.kubeflow.crud_backend import (api, decorators, helpers, logging,
                                            status)
from spire.api.server.agent.v1 import agent_pb2, agent_pb2_grpc

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

    # Hard-coded to use spire-server's unix socket only. Used to get admin access.
    with grpc.insecure_channel("unix:///tmp/spire-server/private/api.sock") as channel:
        stub = agent_pb2_grpc.AgentStub(channel)

        join_token_request = agent_pb2.CreateJoinTokenRequest(ttl=600)
        join_token = stub.CreateJoinToken(join_token_request)

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
    cur.execute(insert_join_token_auth_sql, (new_edge_id, join_token.value))
    db_connection.commit()

    # TODO: Refactor into model
    new_edge = {
        "name": edge_name,
        "namespace": namespace,
        # The status is hardcoded because it is only used for presentation purposes
        "status": status.create_status(status.STATUS_PHASE.READY, "Ready"),
        "age": helpers.get_uptime(created_at),
        "join_token": join_token.value,
    }

    log.info("Successfully created Edge %s/%s", namespace, edge_name)

    return api.success_response("edge", new_edge)
