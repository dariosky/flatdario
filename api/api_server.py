import json
import logging
import os
import collections
from setproctitle import setproctitle

# Compatibility for old Werkzeug/Flask on Python 3.10+
# Older versions import ABCs from collections instead of collections.abc.
def _patch_collections_for_py3():
    import collections.abc as _abc

    for _name in (
        'Container',
        'Iterable',
        'MutableSet',
        'Mapping',
        'MutableMapping',
        'Sequence',
    ):
        if not hasattr(collections, _name):
            setattr(collections, _name, getattr(_abc, _name))


_patch_collections_for_py3()

import flask
from flask import Flask
from flask_cors import CORS
from flask_graphql import GraphQLView
from jinja2 import Environment, PackageLoader, select_autoescape

from api.schema import schema
from api.util.flask_utils import nocache
from storage.sql import StorageSqliteDB, Subscription

try:
    import bjoern
except ImportError:
    bjoern = None

logger = logging.getLogger("flat.api.server")

SERVED_EXTENSIONS = {'.jpg', '.ico', '.png', '.map', '.js', '.svg',
                     '.json', '.css', '.txt'}
service_worker_path = '/custom-service-worker.js'  # this is served with no cache


def get_app(storage, production=True):
    _patch_collections_for_py3()
    setproctitle('api webserver [flatAPI]')
    app = Flask(__name__,
                # static_url_path="",
                static_folder='ui/build',
                template_folder='ui/build')
    CORS(app)

    app.debug = not production
    assert isinstance(storage, StorageSqliteDB)
    db_session = storage.db

    def get_latest_sw():
        latest_file = None
        latest_time = 0
        ui_path = os.path.join(os.path.dirname(__file__), 'ui')
        for path in (
            'build/custom-service-worker.js',
            # 'src/custom-service-worker.js',
        ):
            mtime = os.path.getmtime(
                os.path.join(ui_path, path)
            )
            if mtime > latest_time:
                latest_file = path
                latest_time = mtime
        logger.debug(f"Serviceworker: {latest_file}")
        return latest_file

    latest_sw = get_latest_sw()

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True,  # for having the GraphiQL interface
            context={'session': db_session}
        )
    )

    @app.route("/404/")
    def not_found():
        jinja_env = Environment(
            loader=PackageLoader('api', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

        template = jinja_env.get_template('404.html')
        return template.render(), 404

    @app.route("/push/subscribe", methods=['POST'])
    def subscribe():
        subinfo = flask.request.json
        logger.info(f"Got sub-request: {subinfo}")
        sub_json = json.dumps(subinfo, sort_keys=True)
        subscription = Subscription(
            subscription=sub_json,
            user_agent=flask.request.headers.get('User-Agent')
        )
        db_session.add(subscription)
        db_session.commit()
        return "You subscribed :)"

    @app.route("/push/unsubscribe", methods=['POST'])
    def unsubscribe():
        subinfo = flask.request.json
        sub_json = json.dumps(subinfo, sort_keys=True)
        logger.info(f"Got unsub-request: {subinfo}")
        subscriptions = db_session.query(Subscription).filter_by(
            subscription=sub_json
        )
        if subscriptions.count() != 1:
            return "Cannot unsubscribe", 409
        subscriptions.delete()
        db_session.commit()
        return "You Unsubscribed :)"

    @app.route(service_worker_path)
    @nocache
    def service_worker():
        return flask.send_from_directory('ui', latest_sw)

    @app.route("/", defaults={"url": ""})
    @app.route('/<path:url>')
    def catch_all(url):
        """ Handle the page-not-found - apply some backward-compatibility redirect """
        if url.startswith('getvideo'):
            return flask.redirect('https://getvideo.dariosky.it')
        if url.startswith('home'):
            return flask.redirect('https://home.dariosky.it')
        ext = os.path.splitext(url)[-1]
        if ext in SERVED_EXTENSIONS:
            return flask.send_from_directory('ui/build', url)
        return flask.render_template("index.html")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.close()

    return app


def run_api(storage, host='127.0.0.1', port=3001,
            production=True):
    _patch_collections_for_py3()
    app = get_app(storage, production)
    if production:
        print(f"Running production server as "
              f"{'bjoern' if bjoern else 'Flask'}"
              f" on http://{host}:{port}")
        if bjoern:
            # apt-get install libev-dev
            # apt-get install python3-dev
            print("Running as bjoern")
            bjoern.run(app, host, port)
        else:
            print("Using Flask threaded")
            app.run(host=host, port=port, threaded=True, debug=False, use_reloader=False)
    else:
        print("Running in Flask debug mode")
        app.run(host=host, port=port)
