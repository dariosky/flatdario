"""Serve the current folder to simulate the final webserver"""

import logging

from flask import Flask
from flask import send_from_directory

app = Flask(__name__, static_folder=None)
logger = logging.getLogger(__name__)


@app.route("/", defaults={"path": "/"})
@app.route("/<path:path>")
def send_static(path):
    if path.endswith("/"):
        path += "index.html"
    path = path.lstrip("/")
    served_folder = app.config["SERVED_FOLDER"]
    return send_from_directory(served_folder, path)


@app.errorhandler(404)
def page_not_found(e):
    return (
        "Page not found - this will be the 404 you'll configure on your webserver",
        404,
    )


def serve(path, port=7747):
    app.config["SERVED_FOLDER"] = path
    logger.info("Serving {path}, to get a preview of the content".format(path=path))
    logger.info(
        "Running preview of {path} on http://localhost:{port}".format(
            path=path, port=port
        )
    )
    app.run(host="127.0.0.1", port=port)
