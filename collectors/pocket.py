import datetime
import json
import logging
import os

import pytz
import requests

from .generic import DuplicateFound, OAuthCollector

logger = logging.getLogger(__name__)
requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.WARNING)

session = requests.session()


def get_timestamp_from_epoch(epoch_string):
    epoch_time = int(epoch_string)
    timestamp = datetime.datetime.fromtimestamp(epoch_time, pytz.UTC).isoformat("T") + "Z"
    return timestamp


def get_epoch_from_timestamp(timestamp):
    if isinstance(timestamp, str):
        dt = datetime.datetime.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")
    elif isinstance(timestamp, int):
        return timestamp  # it's already epoch
    else:
        dt = timestamp  # timestamp is a datetime
    epoch = datetime.datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds())


class PocketCollector(OAuthCollector):
    type = 'Pocket'
    api_secrets_file = os.path.join('appkeys', 'pocket.json')
    user_secrets_file = os.path.join("userkeys", "pocket.json")

    def get_endpoints(self):
        return dict(
            request="https://getpocket.com/v3/oauth/request",
            confirmation="https://getpocket.com/auth/authorize?"
                         "request_token={request_token}&redirect_uri={redirect_uri}",
            authenticate="https://getpocket.com/v3/oauth/authorize",
            retrieve="https://getpocket.com/v3/get",
        )

    def get_api_secrets(self):
        try:
            api_secrets = json.load(open(self.api_secrets_file))
        except ValueError:
            logger.error("Cannot read the API secrets for Pocket in %s." % self.api_secrets_file)
            raise
        else:
            return api_secrets

    def initial_parameters(self, db, refresh_duplicates=False, **kwargs):
        """ If we are not refreshing we ask pocket only from the time of last element """
        result = super(PocketCollector, self).initial_parameters(db, refresh_duplicates, **kwargs)
        if not refresh_duplicates:
            max_timestamp = db.max_timestamp(type=self.type)
            result.update(dict(max_timestamp=max_timestamp))
        return result

    def run(self, callback, **params):
        refresh_duplicates = params.pop('refresh_duplicates', False)
        # tried to use the Google OAuth implementation, but:
        # * Pocket does not support GET requests
        # * The Flow is quite not standard
        last_timestamp = params.get('max_timestamp')

        chunk_size = 5
        credentials = self.authenticate()
        endpoints = self.get_endpoints()

        query = dict(
            consumer_key=credentials['consumer_key'],
            access_token=credentials['authentication_token'],
            state="archive",
            sort="newest",
            detailType="complete",
            count=chunk_size,
        )
        if last_timestamp:
            query['since'] = get_epoch_from_timestamp(last_timestamp)

        start_from = 0
        count = 0
        processed = 0

        while True:
            query['offset'] = start_from
            logger.debug("Asking chunk %d-%d" % (start_from, start_from + chunk_size))
            response = session.post(
                endpoints['retrieve'],
                headers={"X-Accept": "application/json"},
                data=query
            )
            if response.status_code != 200:
                raise Exception("Error getting list of items from Pocket")
            data = response.json()
            returned_elements = len(data['list'])
            logger.debug("Pocket query returned %d elements" % returned_elements)
            if data['list']:
                for item_id, e in data['list'].items():
                    # there are other times eventually:
                    #  "time_added", "time_updated", "time_read", "time_favorited"
                    # get the images & video sources, preserving the order
                    images = [e['images'][imgid]['src']
                              for imgid in sorted(list(e.get('images', {}).keys()))
                              ]
                    videos = [e['videos'][imgid]['src']
                              for imgid in sorted(list(e.get('videos', {}).keys()))
                              ]
                    item = dict(
                        id=item_id,
                        type=self.type,
                        url=e['resolved_url'],
                        timestamp=parse_datetime(get_timestamp_from_epoch(e['time_updated'])),
                        timestamp_added=parse_datetime(get_timestamp_from_epoch(e['time_added'])),
                        title=e['resolved_title'],
                        tags=list(e.get('tags', {}).keys()),
                        images=images,
                        videos=videos,
                        excerpt=e['excerpt'],
                    )
                    try:
                        processed += 1
                        callback(item, update=refresh_duplicates)
                        count += 1
                    except DuplicateFound:
                        if not refresh_duplicates:
                            logger.debug("We already know this one.")
                            logger.debug("Stopping after %d added." % count)
                            return
            if returned_elements < chunk_size:
                break
            start_from += chunk_size
        logger.debug("Runner finished, after %d added, %d updated" % (count, processed))


def parse_datetime(timestamp):
    return datetime.datetime.strptime(timestamp,
                                      '%Y-%m-%dT%H:%M:%S+00:00Z')
