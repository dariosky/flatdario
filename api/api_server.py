import flask
from flask import Flask
from flask_cors import CORS
from flask_graphql import GraphQLView

from api.schema import schema
from storage.sql import StorageSqliteDB

try:
    import bjoern
except ImportError:
    bjoern = None

from jinja2 import Environment, PackageLoader, select_autoescape

jinja_env = Environment(
    loader=PackageLoader('api', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def run_api(storage, host='127.0.0.1', port=3001,
            production=True):
    app = Flask(__name__,
                # static_url_path=None,
                static_folder='ui/build',
                template_folder='ui/build')
    CORS(app)

    app.debug = True
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

    @app.route("/")
    def index():
        if not production:
            return flask.redirect('http://localhost:3000')
        return flask.render_template("index.html")

    @app.route('/<path:url>')
    def catch_all(url):
        """ Handle the page-not-found - apply some backward-compatibility redirect """
        if url.startswith('getvideo'):
            return flask.redirect('https://getvideo.dariosky.it')
        if url.startswith('home'):
            return flask.redirect('https://home.dariosky.it')
        template = jinja_env.get_template('404.html')
        return template.render(), 404

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.close()

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
        app.run(host=host, port=port, threaded=True)
