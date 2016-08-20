import json
import logging
import os
import socket

import requests
from oauth2client.tools import ClientRedirectServer, ClientRedirectHandler

from .generic import Collector

logger = logging.getLogger(__name__)


def start_local_server(hostname='localhost', ports=(8080, 8090)):
    for port in ports:
        try:
            httpd = ClientRedirectServer((hostname, port),
                                         ClientRedirectHandler)
        except socket.error:
            pass
        else:
            return httpd


class PocketCollector(Collector):
    type = 'Pocket archived'
    api_secrets_file = os.path.join('appkeys', 'pocket.json')
    user_secrets_file = os.path.join("userkeys", "pocket.json")

    API_ENDPOINTS = dict(
        request="https://getpocket.com/v3/oauth/request",
        confirmation="https://getpocket.com/auth/authorize?" \
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
        request_token = user_secrets.get("request_token")
        access_token = user_secrets.get("access_token")

        if not all([request_token, access_token]):
            logger.debug("Pocket Authentication")

            # Let's start by asking for a new request_token
            response = requests.post(
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
            user_secrets['request_token'] = request_token
            logger.debug("Got request token: %s" % request_token)

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
                logger.info("Opened broser to authorize access: ".format(address=authorize_url))
                server.handle_request()

            # here we got request in the webserver, or the user told us that he granted
            # DONE: we can ask for the access_token
            requests.post(
                self.API_ENDPOINTS['authenticate'],
                headers={"X-Accept": "application/json"},
                data=dict(consumer_key=api_secrets['consumer_key'],
                          code=user_secrets['request_token'],  # Pocket doesn't love standards
                          )
            )
            if response.status_code != 200:
                logger.error("Error getting data from Pocket: %s" % response.text)
                logger.error(response.headers.get('X-Error', 'Pocket error'))
                raise Exception("Cannot get access_token")

            print(response.text)
            # Mmm, documentation says I should receive access_token and username
            user_secrets['access_token'] = response.json()['code']
            # user_secrets['username'] = response.json()['username']
            logger.debug("Got access token: %s" % user_secrets['access_token'])

            # DONE: and save the credentials
            self.save_user_secrets(user_secrets)

        return dict(
            consumer_key=api_secrets['consumer_key'],
            authentication_token=user_secrets['access_token']
        )

    def save_user_secrets(self, user_secrets):
        logger.debug("Saving Pocket client secrets")
        json.dump(user_secrets, open(self.user_secrets_file, 'w'))

    def run(self, callback, **params):
        # tried to use the Google OAuth implementation, but:
        # * Pocket does not support GET requests
        # * The Flow is quite not standard

        credentials = self.authenticate()
        print(credentials)
