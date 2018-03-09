import datetime
import json
import logging
import re

import requests

from collectors.exceptions import DuplicateFound
from collectors.rss import RSSCollector

logger = logging.getLogger(__name__)

TAG_RE = re.compile(r'<[^>]+>')


def strip_tags_from_string(s):
    """ Remove all tags from string """
    if isinstance(s, str):
        return TAG_RE.sub('', s)
    return s


class TumblrCollector(RSSCollector):
    type = 'Tumblr'

    @staticmethod
    def get(url, **feed_kwargs):
        """ Return a function to instanciate the proper collector """

        def instantiator(**call_kwargs):
            kwargs = {**call_kwargs, **feed_kwargs}
            return TumblrCollector(url=url, **kwargs)

        return instantiator

    def run(self, **params):
        logger.debug("Running Tumblr: %s" % self.url)
        endpoint = f'{self.url}/api/read/json'
        start = 0
        count = 0

        while True:
            js_doc = requests.get(
                f"{endpoint}?start={start}"
            ).text

            varvalue = js_doc.replace('var tumblr_api_read = ', '', 1).strip('\n;')
            doc = json.loads(varvalue)

            total = doc['posts-total']

            for entry in doc['posts']:
                entry_date = datetime.datetime.strptime(
                    entry['date-gmt'], '%Y-%m-%d %H:%M:%S GMT'
                )
                url = entry['url-with-slug']  # url to tumblr
                post_type = entry['type']
                content = None

                if post_type == 'video':
                    url = entry['video-source']
                    content = entry['video-player']
                    title = entry['video-caption']
                elif post_type == 'photo':
                    url = entry.get('photo-link-url', url)
                    title = entry['photo-caption']
                    content = f'<img src="{url}" />'
                elif post_type == 'link':
                    title = entry['link-text']
                    url = entry['link-url']
                    content = ''
                elif post_type == 'regular':
                    title = entry['regular-title']
                    content = entry['regular-body']
                elif post_type == 'quote':
                    url = entry['quote-source']
                    title = entry['quote-text']
                else:
                    raise ValueError("Unknown tumblr post type: {post_type}")
                tags = entry.get('tags', [])

                url, title, content = map(
                    strip_tags_from_string,
                    [url, title, content]
                )

                item = dict(
                    type=self.type,
                    id=entry['id'],
                    timestamp=entry_date,
                    url=url,
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
                start += 1
            if start >= total:
                logger.debug("End of the tublr stream")
                break

        logger.debug("Runner finished, after %d added" % count)
