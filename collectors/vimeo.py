import datetime
import json
import logging
import os

import vimeo

from collectors.generic import OAuthCollector
from collectors.exceptions import DuplicateFound

logger = logging.getLogger(__name__)


class VimeoCollector(OAuthCollector):
    type = 'Vimeo'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.vimeo = None

    def authenticate(self):
        api_secrets = self.get_api_secrets()
        user_secrets_file = self.get_user_secrets_filepath()
        user_secrets = dict()
        if os.path.isfile(user_secrets_file):
            try:
                user_secrets = json.load(open(user_secrets_file))
            except ValueError:
                logger.error(
                    f"Cannot read the user secrets for {self.type}"
                    f" in {user_secrets_file}.")
                raise
        access_token = user_secrets.get("access_token")
        auth = dict(
            key=api_secrets['clientID'],
            secret=api_secrets['clientSecrets']
        )
        if access_token:
            auth['token'] = access_token
        self.vimeo = vimeo.VimeoClient(
            **auth
        )
        if not access_token:
            import webbrowser
            server = self.start_local_server()

            if server is None:
                authorize_url = self.vimeo.auth_url(['public', 'private'], '', None)
                logger.warning("Unable to start a localhost webserver to receive the response.")
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
                authorize_url = self.vimeo.auth_url(['public', 'private'], redirect_uri, None)

                webbrowser.open(authorize_url, new=1, autoraise=True)
                logger.info("Opened browser to authorize access: ".format(address=authorize_url))
                server.handle_request()
                token = server.query_params['code']
                try:
                    access_token, user, scope = self.vimeo.exchange_code(token,
                                                                         redirect_uri)
                except vimeo.auth.GrantFailed:
                    raise
                self.save_user_secrets(
                    dict(access_token=access_token)
                )

    def run(self, **params):
        self.authenticate()  # self.vimeo will be ready

        likes = self.vimeo.get('/me/likes')
        count = 0
        while True:
            response = likes.json()
            for video in response['data']:
                assert video['metadata']['interactions']['like']['added'] == True
                liked_timestamp = parse_datetime(
                    video['metadata']['interactions']['like']['added_time']
                )
                logger.debug("{type} - {title} ({id})".format(
                    type=self.type,
                    title=video['name'],
                    id=video['uri']))
                item = dict(
                    id=video['uri'],
                    type=self.type,
                    url=video['link'],
                    timestamp=liked_timestamp,
                    title=video['name'],
                    description=video['description'],
                    thumbnails=video['pictures'],
                    tags=[t['name'] for t in video['tags']],
                )
                try:
                    self.db.upsert(item,
                                   update=self.refresh_duplicates)
                    count += 1
                except DuplicateFound:
                    if not self.refresh_duplicates:
                        logger.debug(
                            "We already know this one. Stopping after %d added." % count)
                        return
            next_page = response['paging']['next']
            if next_page:
                likes = self.vimeo.get(next_page)
            else:
                break

        logger.debug("Runner finished, after %d added" % count)


def parse_datetime(timestamp):
    return datetime.datetime.strptime(timestamp,
                                      '%Y-%m-%dT%H:%M:%S+00:00')
