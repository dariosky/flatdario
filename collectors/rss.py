import datetime
import logging
from time import mktime

import feedparser

from collectors.exceptions import DuplicateFound
from collectors.generic import Collector

logger = logging.getLogger(__name__)


class RSSCollector(Collector):
    type = 'RSS'

    @staticmethod
    def get(url, **feed_kwargs):
        """ Return a function to instanciate the proper collector """

        def instantiator(**call_kwargs):
            kwargs = {**call_kwargs, **feed_kwargs}
            return RSSCollector(url=url, **kwargs)

        return instantiator

    def __init__(self, url, *args, **kwargs) -> None:
        self.url = url
        super().__init__(*args, **kwargs)

    def run(self, **params):
        logger.debug("Running RSS: %s" % self.url)

        doc = feedparser.parse(self.url)
        count = 0
        for entry in doc.entries:
            entry_date = datetime.datetime.fromtimestamp(
                mktime(entry.get('published_parsed', entry['updated_parsed']))
            )
            title = entry['title']
            content = "\n".join([c['value'] for c in entry.get('content', [])])
            tags = [t['term'] for t in entry.get('tags', [])]
            url = entry['link']

            item = dict(
                id=entry['id'],
                type=self.type,
                url=url,
                timestamp=entry_date,
                title=title,
                content=content,
                tags=tags,
            )
            try:
                self.db.upsert(item,
                               update=self.refresh_duplicates)
                logger.info("{type} - {title} ({id})".format(type=self.type,
                                                             title=title, id=url))
                count += 1
            except DuplicateFound:
                if not self.refresh_duplicates:
                    logger.debug(
                        "We already know this one. Stopping after %d added." % count)
                    return

        logger.debug("Runner finished, after %d added" % count)
