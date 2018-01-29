from flask import Flask
from flask_graphql import GraphQLView

from api.schema import schema
from storage.sql import StorageSqliteDB


def run_api(storage, host='127.0.0.1', port=3001):
    app = Flask(__name__)
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

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.close()

    app.run(host=host, port=port)
