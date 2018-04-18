import os
from setproctitle import setproctitle

import flask
from flask import Flask
from flask_cors import CORS
from flask_graphql import GraphQLView
from jinja2 import Environment, PackageLoader, select_autoescape

from api.schema import schema
from storage.sql import StorageSqliteDB

try:
    import bjoern
except ImportError:
    bjoern = None


def get_app(storage, production=True):
    setproctitle('api webserver [flatAPI]')
    app = Flask(__name__,
                # static_url_path="",
                static_folder='ui/build',
                template_folder='ui/build')
    CORS(app)

    app.debug = not production
    assert isinstance(storage, StorageSqliteDB)
    db_session = storage.db

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

    @app.route("/", defaults={"url": ""})
    @app.route('/<path:url>')
    def catch_all(url):
        """ Handle the page-not-found - apply some backward-compatibility redirect """
        if url.startswith('getvideo'):
            return flask.redirect('https://getvideo.dariosky.it')
        if url.startswith('home'):
            return flask.redirect('https://home.dariosky.it')
        ext = os.path.splitext(url)[-1]
        if ext in {'.jpg', '.ico', '.png', '.map', '.js', '.svg', '.json', '.css'}:
            return flask.send_from_directory('ui/build', url)
        return flask.render_template("index.html")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.close()

    return app


def run_api(storage, host='127.0.0.1', port=3001,
            production=True):
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
