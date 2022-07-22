import grpc
from flask import current_app
from kubeflow.kubeflow.crud_backend import api, logging
from spire.api.server.entry.v1 import entry_pb2, entry_pb2_grpc
from spire.api.types import spiffeid_pb2

from ..db import get_db
from . import bp

log = logging.getLogger(__name__)


@bp.route("/api/namespaces/<namespace>/edges/<edge_name>", methods=["DELETE"])
def delete_edge(edge_name, namespace):
    """
    Deregister an edge
    """
    log.info("Deregistering Edge %s/%s...", namespace, edge_name)

    deregister_spire_workloads(
        current_app.config["FL_SUITE_CONFIG"]["fl_edge"]["auth"]["spire"][
            "trust_domain"
        ],
        edge_name,
    )

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


def deregister_spire_workloads(trust_domain: str, edge_name: str):
    # Hard-coded to use spire-server's unix socket only. Used to get admin access.
    with grpc.insecure_channel("unix:///tmp/spire-server/private/api.sock") as channel:
        stub = entry_pb2_grpc.EntryStub(channel)

        edge_spiffe_id = spiffeid_pb2.SPIFFEID(
            trust_domain=trust_domain, path=f"/{edge_name}"
        )

        workload_list_entries_response = stub.ListEntries(
            entry_pb2.ListEntriesRequest(
                filter=entry_pb2.ListEntriesRequest.Filter(by_parent_id=edge_spiffe_id)
            )
        )
        workloads_ids = [entry.id for entry in workload_list_entries_response.entries]

        edge_list_entries_response = stub.ListEntries(
            entry_pb2.ListEntriesRequest(
                filter=entry_pb2.ListEntriesRequest.Filter(by_spiffe_id=edge_spiffe_id)
            )
        )
        edge_ids = [entry.id for entry in edge_list_entries_response.entries]

        batch_delete_request = entry_pb2.BatchDeleteEntryRequest(
            ids=workloads_ids + edge_ids
        )
        stub.BatchDeleteEntry(batch_delete_request)
