import datetime
import json
import logging
import os
import socket

import pytz
import requests

from oauth2client.tools import ClientRedirectServer, ClientRedirectHandler
from tinydb import Query

from .generic import Collector, DuplicateFound

logger = logging.getLogger(__name__)
requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.WARNING)

session = requests.session()


def start_local_server(hostname='localhost', ports=(8080, 8090)):
    for port in ports:
        try:
            httpd = ClientRedirectServer((hostname, port),
                                         ClientRedirectHandler)
        except socket.error:
            pass
        else:
            return httpd


def get_timestamp_from_epoch(epoch_string):
    epoch_time = int(epoch_string)
    timestamp = datetime.datetime.fromtimestamp(epoch_time, pytz.UTC).isoformat("T") + "Z"
    return timestamp


def get_epoch_from_timestamp(timestamp):
    dt = datetime.datetime.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")
    epoch = datetime.datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds())


class PocketCollector(Collector):
    type = 'Pocket archived'
    api_secrets_file = os.path.join('appkeys', 'pocket.json')
    user_secrets_file = os.path.join("userkeys", "pocket.json")

    API_ENDPOINTS = dict(
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

    def authenticate(self):
        # do the authenticate flow if necessary: https://getpocket.com/developer/docs/authentication
        api_secrets = self.get_api_secrets()
        user_secrets = dict()
        if os.path.isfile(self.user_secrets_file):
            try:
                user_secrets = json.load(open(self.user_secrets_file))
            except ValueError:
                logger.error(
                    "Cannot read the user secrets for Pocket in %s." % self.user_secrets_file)
                raise
        access_token = user_secrets.get("access_token")

        if access_token is None:
            logger.debug("Pocket Authentication")

            # Let's start by asking for a new request_token
            response = session.post(
                self.API_ENDPOINTS['request'],
                headers={"X-Accept": "application/json"},
                data=dict(
                    consumer_key=api_secrets['consumer_key'],
                    redirect_uri="http://localhost:8000",
                ))

            if response.status_code != 200:
                logger.error("Error getting data from Pocket: %s" % response.text)
                logger.error(response.headers.get('X-Error', 'Pocket error'))
                raise Exception("Cannot get request_token")

            request_token = response.json()['code']
            # logger.debug("Got request token: %s" % request_token)

            import webbrowser
            server = start_local_server()
            if server is None:
                logger.warning("Unable to start a localhost webserver to receive the response.")
                authorize_url = self.API_ENDPOINTS["confirmation"].format(
                    request_token=request_token,
                    redirect_uri=""
                )
                logger.info(
                    "We open the browser on\n {authorize_url}\nto the authenticate url".format(
                        authorize_url=authorize_url
                    ) +
                    " and ask you to tell us when you have granted the access"
                )
                # logger.info(_GO_TO_LINK_MESSAGE.format(address=authorize_url))
                webbrowser.open(authorize_url, new=1, autoraise=True)
                input('When authorized press enter to continue: ')
            else:
                redirect_uri = 'http://{host}:{port}/'.format(
                    host=server.server_name, port=server.server_port
                )
                authorize_url = self.API_ENDPOINTS["confirmation"].format(
                    request_token=request_token,
                    redirect_uri=redirect_uri
                )

                webbrowser.open(authorize_url, new=1, autoraise=True)
                logger.info("Opened browser to authorize access: ".format(address=authorize_url))
                server.handle_request()

            # here we got request in the webserver, or the user told us that he granted
            # DONE: we can ask for the access_token
            response = session.post(
                self.API_ENDPOINTS['authenticate'],
                headers={"X-Accept": "application/json"},
                data=dict(consumer_key=api_secrets['consumer_key'],
                          code=request_token,  # Pocket doesn't love standards
                          )
            )
            if response.status_code != 200:
                logger.error("Error getting data from Pocket: %s" % response.text)
                logger.error(response.headers.get('X-Error', 'Pocket error'))
                raise Exception("Cannot get access_token")

            data = response.json()
            # logger.debug("Got access_token response: %s" % data)
            user_secrets['access_token'] = data['access_token']
            user_secrets['username'] = data['username']

            # DONE: and save the credentials
            self.save_user_secrets(user_secrets)

        return dict(
            consumer_key=api_secrets['consumer_key'],
            authentication_token=user_secrets['access_token']
        )

    def save_user_secrets(self, user_secrets):
        logger.debug("Saving Pocket client secrets")
        json.dump(user_secrets, open(self.user_secrets_file, 'w'))

    def initial_parameters(self, db, refresh_duplicates=False, **kwargs):
        """ If we are not refreshing we ask pocket only from the time of last element """
        result = super(PocketCollector, self).initial_parameters(db, refresh_duplicates, **kwargs)
        if not refresh_duplicates:
            # we scan all item to get the max_timestamp
            Item = Query()
            items = db.search(Item.type == self.type)
            max_timestamp = None
            for item in items:
                if max_timestamp is None or item['timestamp'] > max_timestamp:
                    max_timestamp = item['timestamp']
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
                self.API_ENDPOINTS['retrieve'],
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
                        timestamp=get_timestamp_from_epoch(e['time_updated']),
                        timestamp_added=get_timestamp_from_epoch(e['time_added']),
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
