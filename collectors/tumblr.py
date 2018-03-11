import datetime
import html
import json
import logging
import re

import requests
from pyquery import PyQuery

from collectors.exceptions import DuplicateFound
from collectors.rss import RSSCollector

logger = logging.getLogger(__name__)

TAG_RE = re.compile(r'<[^>]+>')


def text_from_html(s):
    """ Get text from HTML string, removing all tags"""
    if s is None:
        return None
    result = TAG_RE.sub('', s)
    result = html.unescape(result)
    return result


def get_src_from_iframe(iframe):
    c = PyQuery(iframe)
    result = c('iframe').attr('src')
    return result


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
                context = {'tumblrType': post_type}

                if post_type == 'video':
                    url = entry['video-source']
                    title = entry['video-caption']
                    context['content'] = get_src_from_iframe(entry['video-player'])
                    context['contentFormat'] = 'iframe'
                elif post_type == 'photo':
                    url = entry.get('photo-link-url', url)
                    title = entry['photo-caption']
                    context['img'] = entry['photo-url-1280']
                elif post_type == 'link':
                    url = entry['link-url']
                    title = entry['link-text']
                    context['description'] = text_from_html(entry['link-description'])
                elif post_type == 'regular':
                    title = entry['regular-title']
                    context['subTitle'] = text_from_html(entry['regular-body'])
                elif post_type == 'quote':
                    url = entry['quote-source']
                    title = entry['quote-text']
                else:
                    raise ValueError("Unknown tumblr post type: {post_type}")
                tags = entry.get('tags', [])
                if tags:
                    context['tags'] = tags

                url, title = map(
                    text_from_html,
                    [url, title]
                )

                item = dict(
                    type=self.type,
                    id=entry['id'],
                    timestamp=entry_date,
                    url=url,
                    title=title,

                    **context
                )
                try:
                    self.db.upsert(item,
                                   update=self.refresh_duplicates)
                    logger.info(f"{self.type}-{post_type} - {title} ({url})")
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
