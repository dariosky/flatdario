import logging

from tinydb import TinyDB, Query

from collectors.exceptions import DuplicateFound
from storage import Storage

logger = logging.getLogger(__name__)


class StorageTinyDB(Storage):
    def __init__(self, db_filename):
        super().__init__()
        self.db_filename = db_filename
        self.db = TinyDB(db_filename)

    def search(self, id=None, type=None):
        Item = Query()
        if type and id:
            return self.db.search((Item.id == id) & (Item.type == type))
        elif type:
            return self.db.search(Item.type == type)
        elif id:
            return self.db.search(Item.id == id)

    def upsert(self, item, update=False):
        existing = self.search(id=item['id'], type=item['type'])
        if existing:
            assert len(existing) == 1, \
                'We have 2 duplicates with id: {id} and type: {type}'.format(
                    id=item['id'], type=item['type']
                )
            existing = existing[0]
            if update:
                existing.update(item)
                logger.info("Updating: %s" % item)
                self.db.update(existing, eids=[existing.eid])
            raise DuplicateFound(
                f"We already have the id {item['id']} of type {item['type']} in the DB"
            )
        logger.info('Adding: %s' % item)
        self.db.insert(item)

    def all(self):
        data = self.db.all()
        data.sort(key=lambda item: item['timestamp'], reverse=True)
        return data

    def max_timestamp(self, **kwargs):
        items = self.search(**kwargs)
        # we scan all item to get the max_timestamp
        max_timestamp = None
        for item in items:
            if max_timestamp is None or item['timestamp'] > max_timestamp:
                max_timestamp = item['timestamp']
        return max_timestamp

    def __str__(self):
        return "DB: %s" % self.db_filename

    def close(self):
        pass
