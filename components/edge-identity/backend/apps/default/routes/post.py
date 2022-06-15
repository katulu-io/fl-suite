from datetime import datetime

from flask import request
from kubeflow.kubeflow.crud_backend import api, decorators, logging

from ..db import get_db
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

    db_connection = get_db()
    cur = db_connection.cursor()
    sql = "INSERT INTO Edge(name, namespace, created_at) VALUES(?, ?, ?)"
    cur.execute(sql, (edge_name, namespace, created_at))
    db_connection.commit()

    log.info("Successfully created Edge %s/%s", namespace, edge_name)

    return api.success_response("message", "Edge created successfully.")
