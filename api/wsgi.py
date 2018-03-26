from storage import Storage
from api.api_server import get_app


storage = Storage.get('sqlite', '../db.sqlite')
app = get_app(storage, production=True)
