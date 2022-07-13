from kubeflow.kubeflow.crud_backend import api, logging

from ..db import get_db
from . import bp

log = logging.getLogger(__name__)


@bp.route("/api/namespaces/<namespace>/edges/<edge_name>", methods=["DELETE"])
def delete_edge(edge_name, namespace):
    """
    Deregister an edge
    """
    log.info("Deregistering Edge %s/%s...", namespace, edge_name)

    # TODO: Refactor into model
    db_connection = get_db()
    cur = db_connection.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    sql = "DELETE FROM Edge WHERE name = ? and namespace = ?"
    cur.execute(sql, (edge_name, namespace))
    db_connection.commit()

    log.info("Successfully deregsitered Edge %s/%s", namespace, edge_name)

    return api.success_response(
        "message", "Edge %s successfully deregistered." % edge_name
    )
