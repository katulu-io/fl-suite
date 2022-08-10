from flask import current_app
from kubeflow.kubeflow.crud_backend import api, helpers, logging, status

from ..db import query_db
from . import bp

log = logging.getLogger(__name__)


@bp.route("/api/namespaces/<namespace>/edges")
def get_edges(namespace):
    edge_list = []

    # TODO: Refactor into model
    results = query_db(
        "SELECT "
        "e.edge_id, e.name, e.namespace, e.created_at, a.join_token "
        "FROM Edge AS e join JoinTokenAuth as a ON a.edge_id = e.edge_id "
        "WHERE e.namespace = ?;",
        (namespace,),
    )
    spire_config = current_app.config["FL_SUITE_CONFIG"]["fl_edge"]["auth"]["spire"]
    fl_operator_config = current_app.config["FL_SUITE_CONFIG"]["fl_operator"]
    if results is not None:
        for edge in results:
            edge_dict = {
                "name": edge["name"],
                "namespace": edge["namespace"],
                # The status is hardcoded because it is only used for presentation purposes
                "status": status.create_status(status.STATUS_PHASE.READY, "Ready"),
                "age": helpers.get_uptime(edge["created_at"]),
                "join_token": edge["join_token"],
            }
            edge_dict.update(spire_config)
            edge_dict.update(fl_operator_config)
            edge_list.append(edge_dict)

    return api.success_response("edges", edge_list)
