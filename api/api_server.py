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


def run_api(storage, host='127.0.0.1', port=3001,
            production=True):
    app = Flask(__name__,
                static_url_path="",
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
        return flask.render_template("index.html")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.close()

    if production and bjoern:
        print(f"Running production server on http://{host}:{port}")
        if bjoern:
            # apt-get install libev-dev
            # apt-get install python3-dev
            bjoern.run(app, host, port)
        else:
            app.run(host=host, port=port, threaded=True, debug=False, reload=False)
    else:
        # flask runserver
        app.run(host=host, port=port, threaded=True)
