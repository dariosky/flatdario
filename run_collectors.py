import logging
import os
import sys

import httplib2
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from tinydb import Query
from tinydb import TinyDB

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DuplicateFound(Exception):
    pass


class Collector(object):
    def process_record(self, item):
        raise NotImplemented

    def initial_parameters(self, db):
        """ Given the DB return the initial parameters to be passed to the collector....
            for example to tell him where to start
            :rtype: dict
            :type db: TinyDB
        """
        return dict()

    def run(self, callback, **params):
        raise NotImplemented


class YouTubeLikesCollector(Collector):
    CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "client_secrets.json")
    YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    type = 'Youtube like'

    def run(self, callback, **params):
        flow = flow_from_clientsecrets(
            self.CLIENT_SECRETS_FILE,
            message="You need the %s file with your app credentials" % self.CLIENT_SECRETS_FILE,
            scope=self.YOUTUBE_READONLY_SCOPE)

        storage = Storage("client-youtube-oauth2.json")
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            flags = argparser.parse_args()
            credentials = run_flow(flow, storage, flags)

        youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
                        http=credentials.authorize(httplib2.Http()))

        channels_response = youtube.channels().list(
            mine=True,
            part="contentDetails"
        ).execute()

        ignore_duplicates = params.pop('ignore_duplicates', False)
        last_video_id = params.pop('last_id', None)
        logger.debug(
            "Running %s collector." % self.type + "until %s" % last_video_id if last_video_id else ""
        )

        count = 0
        for channel in channels_response["items"]:
            likes_list_id = channel['contentDetails']['relatedPlaylists']['likes']

            playlistitems_list_request = youtube.playlistItems().list(
                playlistId=likes_list_id,
                part="snippet",
                maxResults=5
            )

            while playlistitems_list_request:
                playlistitems_list_response = playlistitems_list_request.execute()

                # Print information about each video.
                for playlist_item in playlistitems_list_response["items"]:
                    snippet = playlist_item["snippet"]
                    title = snippet["title"]
                    video_id = snippet["resourceId"]["videoId"]
                    if not 'thumbnails' in snippet:
                        logger.debug(
                            "Skipping video {title} ({id})".format(title=title, id=video_id))
                        continue

                    timestamp = snippet['publishedAt']
                    description = snippet['description']
                    thumbnails = snippet['thumbnails']

                    logger.info("{type} - {title} ({id})".format(type=self.type,
                                                                 title=title, id=video_id))
                    item = dict(
                        id=video_id,
                        type=self.type,
                        timestamp=timestamp,
                        description=description,
                        thumbnails=thumbnails,
                    )
                    try:
                        count += 1
                        callback(item, update=ignore_duplicates)
                    except DuplicateFound:
                        if not ignore_duplicates:
                            logger.debug("We already know this one. Stopping.")
                            return

                playlistitems_list_request = youtube.playlistItems().list_next(
                    playlistitems_list_request,
                    playlistitems_list_response)
        logger.info("Runner finished, after %d elements" % count)

    def initial_parameters(self, db):
        result = super(YouTubeLikesCollector, self).initial_parameters(db)

        if False:
            Item = Query()
            items = db.search(Item.type == self.type)
            max_timestamp = None
            max_id = None
            for item in items:
                if max_timestamp is None or item['timestamp'] > max_timestamp:
                    max_timestamp = item['timestamp']
                    max_id = item['id']
            result.update(dict(last_id=max_id))
        return result


class Aggregator(object):
    collectors = [
        YouTubeLikesCollector,
    ]

    def __init__(self):
        super(Aggregator, self).__init__()
        self.db = TinyDB('db.json')

    def save_item(self, item, update=False):
        Item = Query()
        existing = self.db.get((Item.id == item['id']) & (Item.type == item['type']))
        if existing:
            if update:
                existing.update(item)
            raise DuplicateFound('We already have the id %s of type %s in the DB')
        logger.debug('adding: %s' % item)
        self.db.insert(item)

    def collect(self):
        logger.info("Running the Collector")
        for collector_class in self.collectors:
            collector = collector_class()
            initial_collect_params = collector.initial_parameters(self.db)
            collector.run(callback=self.save_item,
                          ignore_duplicates=False,
                          **initial_collect_params)


if __name__ == '__main__':
    agg = Aggregator()
    agg.collect()
