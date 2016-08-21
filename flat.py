#!/usr/bin/env python
import argparse
import logging

import datetime
from tinydb import Query
from tinydb import TinyDB

from collectors import *
from collectors.generic import DuplicateFound

logger = logging.getLogger(__name__)
VERSION = "0.1"


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


def get_options():
    parser = argparse.ArgumentParser(
        "FlatDario",
        description="Aggregate your social activities in a simple fast static flat site"
    )
    parser.add_argument("-v", "--version", action="version", version=VERSION)
    parser.add_argument("--debug",
                        help="Run in debug mode, verbose output is shown",
                        default=False,
                        action="store_true")
    parser.add_argument("--update",
                        help="Scan all the elements and update them instead of doing an incremental sync",
                        default=False,
                        action="store_true")
    parser.add_argument("--nocollect",
                        help="Avoid the collection phase, just update the flatsite from DB",
                        default=False,
                        action="store_true")
    return parser.parse_args()


if __name__ == '__main__':
    print("FlatDario %s" % VERSION)
    print("Copyright (C) 2015-%s  Dario Varotto\n" % datetime.date.today().year)

    args = get_options()

    # configure logging level
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    agg = Aggregator()
    if not args.nocollect:
        agg.collect(
            refresh_duplicates=args.update
        )
