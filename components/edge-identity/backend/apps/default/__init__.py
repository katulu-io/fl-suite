import json
import os
from typing import Optional

import kubeflow.kubeflow.crud_backend as base
from kubeflow.kubeflow.crud_backend import config, logging

from . import db
from .routes import bp as routes_bp

log = logging.getLogger(__name__)


def create_app(
    name=__name__, cfg: config.Config = None, fl_suite_config_path: Optional[str] = None
):
    cfg = config.Config() if cfg is None else cfg

    # Properly set the static serving directory
    static_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static")

    cfg = config.Config() if cfg is None else cfg

    app = base.create_app(name, static_dir, cfg)

    log.info("Setting STATIC_DIR to: " + static_dir)
    app.config["STATIC_DIR"] = static_dir
    if fl_suite_config_path is None:
        app.config["FL_SUITE_CONFIG"] = DEFAULT_FL_SUITE_CONFIG
    else:
        with open(fl_suite_config_path, "r") as f:
            app.config["FL_SUITE_CONFIG"] = json.load(f)

    # Register the app's blueprints
    app.register_blueprint(routes_bp)
    db.init_app(app)

    return app


DEFAULT_FL_SUITE_CONFIG = {
    "fl_edge": {
        "auth": {
            "spire": {
                "server_address": "spire-server.spire.svc.cluster.local",
                "server_port": 8081,
                "trust_domain": "katulu.io",
                "skip_kubelet_verification": True,
            }
        }
    },
    "fl_operator": {
        "orchestrator_url": "istio-ingressgateway.istio-system.svc.cluster.local",
        "orchestrator_port": 443,
        "orchestrator_sni": "fl-orchestrator.fl-suite",
    },
}
