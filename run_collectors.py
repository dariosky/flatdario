import logging

from tinydb import Query
from tinydb import TinyDB

from collectors import *
from collectors.generic import DuplicateFound

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Aggregator(object):
    collectors = [
        # YouTubeLikesCollector,
        PocketCollector,
    ]

    def __init__(self):
        super(Aggregator, self).__init__()
        self.db = TinyDB('db.json')

    def save_item(self, item, update=False):
        Item = Query()
        existing = self.db.search((Item.id == item['id']) & (Item.type == item['type']))
        if existing:
            assert len(existing) == 1, 'We have 2 duplicates with id: {id} and type: {type}'.format(
                id=item['id'], type=item['type']
            )
            existing = existing[0]
            if update:
                existing.update(item)
                self.db.update(existing, eids=[existing.eid])
            raise DuplicateFound('We already have the id %s of type %s in the DB')
        logger.debug('adding: %s' % item)
        self.db.insert(item)

    def collect(self, refresh_duplicates=False):
        logger.info("Running the Collectors")
        for collector_class in self.collectors:
            logger.info(collector_class.__name__)
            collector = collector_class()
            # we can decide the initial collect parameter looking at the DB?
            initial_collect_params = collector.initial_parameters(
                self.db,
                refresh_duplicates=refresh_duplicates
            )
            # Run the collector
            collector.run(callback=self.save_item,
                          refresh_duplicates=refresh_duplicates,
                          **initial_collect_params)


if __name__ == '__main__':
    agg = Aggregator()
    agg.collect(
        refresh_duplicates=False
    )
