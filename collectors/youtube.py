import datetime
import logging
import os
from argparse import Namespace

import httplib2
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from .exceptions import DuplicateFound
from .generic import Collector

logger = logging.getLogger(__name__)

DATE_FORMATS = ('%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                )


def parse_datetime(timestamp):
    for date_format in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(timestamp, date_format)
        except ValueError:
            pass
    raise ValueError(f"Cannot find a valid format for {timestamp}")


class YouTubeLikesCollector(Collector):
    CLIENT_SECRETS_FILE = os.path.join("appkeys", "google.json")
    YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    type = 'Youtube'
    subtype = 'like'

    def get_credentials(self):
        flow = flow_from_clientsecrets(
            self.CLIENT_SECRETS_FILE,
            message="You need the %s file with your app credentials" % self.CLIENT_SECRETS_FILE,
            scope=self.YOUTUBE_READONLY_SCOPE)
        storage = Storage(os.path.join("userkeys", "google.json"))
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            flags = Namespace(
                logging_level='ERROR',
                auth_host_name='localhost',
                noauth_local_webserver=False,
                auth_host_port=[8080, 8090],
            )
            credentials = run_flow(flow, storage, flags=flags)
        return credentials

    def run(self, **params):
        refresh_duplicates = self.refresh_duplicates
        credentials = self.get_credentials()

        youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
                        http=credentials.authorize(httplib2.Http()),
                        cache_discovery=False,  # cache is disabled with oauthclient >= 4.0.0
                        )

        logger.debug("Running %s collector." % self.type)

        channels_response = youtube.channels().list(
            mine=True,
            part="contentDetails"
        ).execute()

        count = 0
        for channel in channels_response["items"]:
            list_id = self.get_list_id(channel)

            playlistitems_list_request = youtube.playlistItems().list(
                playlistId=list_id,
                part="snippet,status",
                maxResults=5
            )

            while playlistitems_list_request:
                playlistitems_list_response = playlistitems_list_request.execute()

                # Print information about each video.
                for playlist_item in playlistitems_list_response["items"]:
                    if playlist_item['status']['privacyStatus'] in ('unlisted', 'private'):
                        # ignore unlisted
                        continue
                    snippet = playlist_item["snippet"]
                    title = snippet["title"]
                    video_id = snippet["resourceId"]["videoId"]
                    if 'thumbnails' not in snippet:
                        logger.debug(
                            "Skipping video {title} ({id})".format(title=title, id=video_id))
                        continue

                    timestamp = parse_datetime(snippet['publishedAt'])
                    description = snippet['description']
                    thumbnails = snippet['thumbnails']

                    item = dict(
                        id=video_id,
                        type=self.type,
                        subtype=self.subtype,
                        url="https://www.youtube.com/watch?v=%s" % video_id,
                        timestamp=timestamp,
                        title=title,
                        description=description,
                        thumbnails=thumbnails,
                    )
                    try:
                        item['thumb'] = item['thumbnails']['medium']['url']
                    except:
                        pass
                    try:
                        self.db.upsert(item, update=refresh_duplicates)
                        logger.info("{type} - {title} ({id})".format(type=self.type,
                                                                     title=title, id=video_id))
                        count += 1
                    except DuplicateFound:
                        if not refresh_duplicates:
                            logger.debug(
                                "We already know this one. Stopping after %d added." % count)
                            return

                playlistitems_list_request = youtube.playlistItems().list_next(
                    playlistitems_list_request,
                    playlistitems_list_response)
        logger.debug("Runner finished, after %d added" % count)

    def get_list_id(self, channel):
        return channel['contentDetails']['relatedPlaylists']['likes']


# unfortunately since Sept.15, 2016 the watchLater playlist doesn't return items anymore

class YouTubeMineCollector(YouTubeLikesCollector):
    type = 'Youtube'
    subtype = 'upload'

    def get_list_id(self, channel):
        return channel['contentDetails']['relatedPlaylists']['uploads']
