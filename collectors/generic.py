import json
import logging
import os
import socket

import requests
from oauth2client.tools import (ClientRedirectServer,
                                ClientRedirectHandler)

muted_loggers = (
    'googleapiclient.discovery',
    'oauth2client',
    'requests',
    'urllib3',
    'watchdog',
    'PIL',
)

for logger_name in muted_loggers:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class Collector:
    type = 'Collectory Type not specified'

    def __init__(self, refresh_duplicates, db=None):
        self.refresh_duplicates = refresh_duplicates
        self.db = db

    def initial_parameters(self, **kwargs):
        """ Given the DB return the initial parameters to be passed to the collector....
            for example to tell him where to start
            :rtype: dict
            :type db: Storage
        """
        return dict()

    def run(self, **params):
        raise NotImplementedError("Collectors should define what to do on run method")


class OAuthCollector(Collector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = requests.session()

    def get_api_secrets(self):
        api_secrets_file = self.get_api_secrets_filepath()
        try:
            api_secrets = json.load(open(api_secrets_file))
        except ValueError:
            logger.error(f"Cannot read the API secrets for {self.type} in {api_secrets_file}.")
            raise
        else:
            return api_secrets

    def get_endpoints(self):
        endpoints = dict(
            request=".../oauth/request",
            confirmation="../auth/authorize?"
                         "request_token={request_token}&redirect_uri={redirect_uri}",
            authenticate=".../v3/oauth/authorize",
            retrieve=".../v3/get",
        )
        raise NotImplementedError("Collectors should define the endpoints for oAuth.\n"
                                  "Something like %s" % endpoints)

    @staticmethod
    def start_local_server(hostname='localhost', ports=(8080, 8090)):
        for port in ports:
            try:
                httpd = ClientRedirectServer((hostname, port),
                                             ClientRedirectHandler)
            except socket.error:
                pass
            else:
                return httpd

    def save_user_secrets(self, user_secrets):
        logger.debug(f"Saving {self.type} client secrets")
        json.dump(user_secrets, open(self.get_user_secrets_filepath(), 'w'))

    def authenticate(self):
        api_secrets = self.get_api_secrets()

        user_secrets_file = self.get_user_secrets_filepath()
        user_secrets = dict()
        endpoints = self.get_endpoints()
        if os.path.isfile(user_secrets_file):
            try:
                user_secrets = json.load(open(user_secrets_file))
            except ValueError:
                logger.error(
                    f"Cannot read the user secrets for {self.type} in {user_secrets_file}.")
                raise
        access_token = user_secrets.get("access_token")

        if access_token is None:
            logger.debug(f"{self.type} Authentication")

            # Let's start by asking for a new request_token
            response = self.session.post(
                endpoints['request'],
                headers={"X-Accept": "application/json"},
                data=dict(
                    consumer_key=api_secrets['consumer_key'],
                    redirect_uri="http://localhost:8000",
                ))

            if response.status_code != 200:
                logger.error(f"Error getting data from {self.type}: %s" % response.text)
                logger.error(response.headers.get('X-Error', f'{self.type} error'))
                raise Exception("Cannot get request_token")

            request_token = response.json()['code']
            # logger.debug("Got request token: %s" % request_token)

            import webbrowser
            server = self.start_local_server()
            if server is None:
                logger.warning("Unable to start a localhost webserver to receive the response.")
                authorize_url = endpoints["confirmation"].format(
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
                authorize_url = endpoints["confirmation"].format(
                    request_token=request_token,
                    redirect_uri=redirect_uri
                )

                webbrowser.open(authorize_url, new=1, autoraise=True)
                logger.info("Opened browser to authorize access: ".format(address=authorize_url))
                server.handle_request()

            # here we got request in the webserver, or the user told us that he granted
            # DONE: we can ask for the access_token
            response = self.session.post(
                endpoints['authenticate'],
                headers={"X-Accept": "application/json"},
                data=dict(consumer_key=api_secrets['consumer_key'],
                          code=request_token,  # Pocket doesn't love standards
                          )
            )
            if response.status_code != 200:
                logger.error(f"Error getting data from f{self.type}: %s" % response.text)
                logger.error(response.headers.get('X-Error', f'{self.type} error'))
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

    def get_user_secrets_filepath(self):
        collectory_type = self.type.lower()
        return os.path.join("userkeys", f"{collectory_type}.json")

    def get_api_secrets_filepath(self):
        collectory_type = self.type.lower()
        api_secrets_file = os.path.join('appkeys', f'{collectory_type}.json')
        return api_secrets_file

    def run(self, **params):
        raise NotImplementedError()
