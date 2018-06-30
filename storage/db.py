import logging

logger = logging.getLogger(__name__)


class Storage:
    @staticmethod
    def get(db_format, db_filename):
        if db_format == 'json':
            from .json import StorageTinyDB
            db = StorageTinyDB(db_filename=db_filename)
        elif db_format == 'sqlite':
            from .sql import StorageSqliteDB
            db = StorageSqliteDB(db_filename)
        else:
            db = Storage()
        return db

    def search(self, id, type):
        raise NotImplementedError()

    def all(self):
        raise NotImplementedError()

    def getitem(self, item_id):
        raise NotImplementedError()

    def upsert(self, item, update=False):
        raise NotImplementedError

    def max_timestamp(self, **kwargs):
        raise NotImplementedError

    # generic ***

    def close(self):
        raise NotImplementedError

    # push notifications ***

    def active_subscriptions(self):
        """ Return all the active push subscription """
        raise NotImplementedError()

    def set_last_notification(self, subscription):
        """ Mark the time when the subscription got last notified """
        raise NotImplementedError()
