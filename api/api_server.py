import json
import logging
import os
import collections
from functools import wraps
from setproctitle import setproctitle


from api.util.compat import patch_collections_for_py3
from flat import _patch_collections_for_py3

patch_collections_for_py3()

import flask
from flask import Flask, session, jsonify
from flask_cors import CORS
from flask_graphql import GraphQLView
from graphql_relay import from_global_id, to_global_id
from jinja2 import Environment, PackageLoader, select_autoescape
from werkzeug.security import check_password_hash

from api.schema import schema
from api.util.flask_utils import nocache
from storage.sql import StorageSqliteDB, Subscription, Item, User
from collectors.manual import build_item_from_url

try:
    import bjoern
except ImportError:
    bjoern = None

logger = logging.getLogger("flat.api.server")

SERVED_EXTENSIONS = {
    ".jpg",
    ".ico",
    ".png",
    ".map",
    ".js",
    ".svg",
    ".json",
    ".css",
    ".txt",
    ".xml",
}
service_worker_path = "/custom-service-worker.js"  # this is served with no cache


def get_app(storage, production=True):
    patch_collections_for_py3()
    setproctitle("api webserver [flatAPI]")
    app = Flask(
        __name__,
        # static_url_path="",
        static_folder="ui/build",
        template_folder="ui/build",
    )
    CORS(
        app,
        supports_credentials=True,
        origins=[
            "http://127.0.0.1:3000",
            "http://localhost:3000",
        ],
    )
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me")

    app.debug = not production
    assert isinstance(storage, StorageSqliteDB)
    db_session = storage.db

    def get_latest_sw():
        latest_file = None
        latest_time = 0
        ui_path = os.path.join(os.path.dirname(__file__), "ui")
        for path in (
            "build/custom-service-worker.js",
            # 'src/custom-service-worker.js',
        ):
            mtime = os.path.getmtime(os.path.join(ui_path, path))
            if mtime > latest_time:
                latest_file = path
                latest_time = mtime
        logger.debug(f"Serviceworker: {latest_file}")
        return latest_file

    latest_sw = get_latest_sw()

    app.add_url_rule(
        "/graphql",
        view_func=GraphQLView.as_view(
            "graphql",
            schema=schema,
            graphiql=True,  # for having the GraphiQL interface
            context={"session": db_session, "flask_session": flask.session},
        ),
    )

    def is_admin():
        return session.get("admin") is True

    def normalize_item_id(item_id):
        try:
            decoded_type, decoded_id = from_global_id(item_id)
            # ensure we decoded something meaningful
            if decoded_id:
                return decoded_id
        except Exception:
            pass
        return item_id

    def admin_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not is_admin():
                return jsonify({"error": "unauthorized"}), 401
            return fn(*args, **kwargs)

        return wrapper

    @app.route("/auth/login", methods=["POST"])
    def login():
        data = flask.request.json or {}
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"error": "missing credentials"}), 400
        user = db_session.query(User).filter_by(name=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "invalid credentials"}), 401
        session["admin"] = True
        session["user"] = username
        logger.info(f"Login success for user {username}")
        return jsonify({"ok": True, "user": username})

    @app.route("/auth/logout", methods=["POST"])
    def logout():
        logger.info(f"Logout for user {session.get('user')}")
        session.clear()
        return jsonify({"ok": True})

    @app.route("/auth/me", methods=["GET"])
    def me():
        return jsonify({"authenticated": is_admin(), "user": session.get("user")})

    @app.route("/admin/items/<item_id>/hide", methods=["POST"])
    @admin_required
    def hide_item(item_id):
        data = flask.request.json or {}
        hidden = bool(data.get("hidden", True))
        db_id = normalize_item_id(item_id)
        item = db_session.query(Item).get(db_id)
        if not item:
            return jsonify({"error": "not found"}), 404
        item.hidden = hidden
        db_session.commit()
        return jsonify({"id": item_id, "hidden": item.hidden})

    @app.route("/admin/items/<item_id>", methods=["DELETE"])
    @admin_required
    def delete_item(item_id):
        db_id = normalize_item_id(item_id)
        item = db_session.query(Item).get(db_id)
        if not item:
            return jsonify({"error": "not found"}), 404
        db_session.delete(item)
        db_session.commit()
        return jsonify({"deleted": True, "id": item_id})

    @app.route("/admin/items/<item_id>", methods=["GET"])
    @admin_required
    def get_item(item_id):
        db_id = normalize_item_id(item_id)
        item = db_session.query(Item).get(db_id)
        if not item:
            return jsonify({"error": "not found"}), 404
        return jsonify(
            {
                "id": item.id,
                "type": item.type,
                "title": item.title,
                "url": item.url,
                "timestamp": item.timestamp.isoformat() if item.timestamp else None,
                "hidden": bool(item.hidden),
                "extra": item.extra or "{}",
            }
        )

    @app.route("/admin/items/<item_id>", methods=["PUT"])
    @admin_required
    def update_item(item_id):
        data = flask.request.json or {}
        db_id = normalize_item_id(item_id)
        item = db_session.query(Item).get(db_id)
        if not item:
            return jsonify({"error": "not found"}), 404
        extra_raw = data.get("extra", "{}")
        try:
            extra_obj = json.loads(extra_raw) if isinstance(extra_raw, str) else extra_raw
            extra_json = json.dumps(extra_obj)
        except Exception:
            return jsonify({"error": "invalid extra json"}), 400
        title = data.get("title")
        url = data.get("url")
        if title:
            item.title = title
        if url:
            item.url = url
        item.extra = extra_json
        db_session.commit()
        return jsonify({"ok": True, "id": item_id})

    @app.route("/admin/items", methods=["POST"])
    @admin_required
    def create_item():
        data = flask.request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "missing url"}), 400
        try:
            item = build_item_from_url(url)
            storage.upsert(item, update=True)
            global_id = to_global_id("ItemType", item["id"])
            return jsonify({"ok": True, "id": global_id})
        except Exception as exc:
            logger.exception("Failed to create item from url")
            return jsonify({"error": str(exc)}), 500

    @app.route("/404/")
    def not_found():
        jinja_env = Environment(
            loader=PackageLoader("api", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )

        template = jinja_env.get_template("404.html")
        return template.render(), 404

    @app.route("/push/subscribe", methods=["POST"])
    def subscribe():
        subinfo = flask.request.json
        logger.info(f"Got sub-request: {subinfo}")
        sub_json = json.dumps(subinfo, sort_keys=True)
        subscription = Subscription(
            subscription=sub_json, user_agent=flask.request.headers.get("User-Agent")
        )
        db_session.add(subscription)
        db_session.commit()
        return "You subscribed :)"

    @app.route("/push/unsubscribe", methods=["POST"])
    def unsubscribe():
        subinfo = flask.request.json
        sub_json = json.dumps(subinfo, sort_keys=True)
        logger.info(f"Got unsub-request: {subinfo}")
        subscriptions = db_session.query(Subscription).filter_by(subscription=sub_json)
        if subscriptions.count() != 1:
            return "Cannot unsubscribe", 409
        subscriptions.delete()
        db_session.commit()
        return "You Unsubscribed :)"

    @app.route(service_worker_path)
    @nocache
    def service_worker():
        return flask.send_from_directory("ui", latest_sw)

    @app.route("/", defaults={"url": ""})
    @app.route("/<path:url>")
    def catch_all(url):
        """Handle the page-not-found - apply some backward-compatibility redirect"""
        if url.startswith("getvideo"):
            return flask.redirect("https://getvideo.dariosky.it")
        if url.startswith("home"):
            return flask.redirect("https://home.dariosky.it")
        ext = os.path.splitext(url)[-1]

        # If the URL looks like a detail page, return 404 when the item is missing
        if url.startswith("view/"):
            item_id = url.split("/", 1)[-1]
            if not item_id:
                return flask.render_template("index.html"), 404
            db_id = normalize_item_id(item_id)
            exists = db_session.query(Item.id).filter_by(id=db_id).first()
            if not exists:
                return flask.render_template("index.html"), 404
            if not is_admin():
                hidden = db_session.query(Item.hidden).filter_by(id=db_id).scalar()
                if hidden:
                    return flask.render_template("index.html"), 404

        if ext in SERVED_EXTENSIONS:
            return flask.send_from_directory("ui/build", url)
        return flask.render_template("index.html")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.close()

    return app


def run_api(storage, host="127.0.0.1", port=3001, production=True):
    _patch_collections_for_py3()
    app = get_app(storage, production)
    if production:
        print(
            f"Running production server as "
            f"{'bjoern' if bjoern else 'Flask'}"
            f" on http://{host}:{port}"
        )
        if bjoern:
            # apt-get install libev-dev
            # apt-get install python3-dev
            print("Running as bjoern")
            bjoern.run(app, host, port)
        else:
            print("Using Flask threaded")
            app.run(
                host=host, port=port, threaded=True, debug=False, use_reloader=False
            )
    else:
        print("Running in Flask debug mode")
        app.run(host=host, port=port)
