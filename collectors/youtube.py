import logging
import os

import httplib2
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

from .generic import Collector, DuplicateFound

logger = logging.getLogger(__name__)
gapi_logger = logging.getLogger('googleapiclient.discovery')
gapi_logger.setLevel(logging.WARNING)


class YouTubeLikesCollector(Collector):
    CLIENT_SECRETS_FILE = os.path.join("appkeys", "google.json")
    YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    type = 'Youtube like'

    def get_credentials(self):
        flow = flow_from_clientsecrets(
            self.CLIENT_SECRETS_FILE,
            message="You need the %s file with your app credentials" % self.CLIENT_SECRETS_FILE,
            scope=self.YOUTUBE_READONLY_SCOPE)
        storage = Storage(os.path.join("userkeys", "google.json"))
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            flags = argparser.parse_args()
            credentials = run_flow(flow, storage, flags)
        return credentials

    def run(self, callback, **params):
        refresh_duplicates = params.pop('refresh_duplicates', False)
        credentials = self.get_credentials()

        youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
                        http=credentials.authorize(httplib2.Http()))

        channels_response = youtube.channels().list(
            mine=True,
            part="contentDetails"
        ).execute()

        last_video_id = params.pop('last_id', None)
        logger.debug(
            "Running %s collector." % self.type +
            "until %s" % last_video_id if last_video_id else ""
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
                    if 'thumbnails' not in snippet:
                        logger.debug(
                            "Skipping video {title} ({id})".format(title=title, id=video_id))
                        continue

                    timestamp = snippet['publishedAt']
                    description = snippet['description']
                    thumbnails = snippet['thumbnails']

                    logger.debug("{type} - {title} ({id})".format(type=self.type,
                                                                 title=title, id=video_id))
                    item = dict(
                        id=video_id,
                        type=self.type,
                        url="https://www.youtube.com/watch?v=%s" % video_id,
                        timestamp=timestamp,
                        title=title,
                        description=description,
                        thumbnails=thumbnails,
                    )
                    try:
                        callback(item, update=refresh_duplicates)
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
