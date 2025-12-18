from api.api_server import get_app
from storage import Storage

storage = Storage.get("sqlite", "../db.sqlite")
app = get_app(storage, production=True)
