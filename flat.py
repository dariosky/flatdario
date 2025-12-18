#!/usr/bin/env python
import argparse
import datetime
import json
import logging
import os
import sys
import textwrap
import collections


def _patch_collections_for_py3():
    """Compatibility shim for libraries that import ABCs from collections."""
    import collections.abc as _abc

    for _name in (
        "Container",
        "Iterable",
        "MutableSet",
        "Mapping",
        "MutableMapping",
        "Sequence",
    ):
        if not hasattr(collections, _name):
            setattr(collections, _name, getattr(_abc, _name))


_patch_collections_for_py3()

from sing import single

from collectors import *
from collectors.rss import RSSCollector
from collectors.scrapers.grab_opengraph import fill_missing_infos
from collectors.youtube import YouTubeMineCollector
from flatbuilder.builder import Builder, Template, NotATemplateFolder
from flatbuilder.preview import serve
from storage import Storage

logger = logging.getLogger(__name__)
VERSION = "1.1"
TEMPLATE_CONTAINER_FOLDER = "flatbuilder"
PROJECT_PATH = os.path.dirname(__file__)
os.chdir(PROJECT_PATH)


class Aggregator:
    collectors = [
        YouTubeMineCollector,
        YouTubeLikesCollector,
        PocketCollector,
        VimeoCollector,
        RSSCollector.get(url="https://dariosky.github.io/rss/index.rss"),
        RSSCollector.get(
            url="http://rss.dariosky.it/public.php?op=rss&id=-2&key=bbwf1t5a80b21066d41"
        ),
        RSSCollector.get(
            url="https://www.reddit.com/saved.rss?"
            "feed=a5174816204085b3bdd43e2df8f8e93ee98c7a1a&user=dariosky"
        ),
        # TumblrCollector.get('https://tumblr.dariosky.it'),
    ]

    def __init__(self):
        super(Aggregator, self).__init__()
        config = self.load_config()
        c = config.get
        self.db_filename = c("db", "db.json")
        self.db_format = c("format", "json")
        self.build_template = c("template", "empty")

        self.db = Storage.get(self.db_format, self.db_filename)

    @staticmethod
    def load_config(config_file=os.path.join(PROJECT_PATH, "flat.json")):
        if os.path.isfile(config_file):
            logger.debug(f"Getting configuration from {config_file}")
            with open(config_file, "r", encoding="utf8") as f:
                return json.load(f)
        return {}

    def collect(self, refresh_duplicates=False):
        logger.info("Running the Collectors")
        for collector_class in self.collectors:
            logger.debug(collector_class.__name__)
            collector = collector_class(
                refresh_duplicates=refresh_duplicates,
                db=self.db,
            )
            # we can decide the initial collect parameter looking at the DB?
            initial_collect_params = collector.initial_parameters()
            # Run the collector
            collector.run(**initial_collect_params)
        fill_missing_infos(self.db)
        self.db.close()

    def build(self, folder="build"):
        if not os.path.isdir(folder):
            logger.warning("Build target folder '%s' not found." % folder)
            logger.warning("Create it from a template with the 'init' action.")
            sys.exit(1)
        logger.info("Building the static site")
        logger.info("  DB: %s" % self.db)
        logger.info("  target folder: %s" % folder)

        builder = Builder()
        builder.run(items=self.db.all(), folder=folder)

    @staticmethod
    def preview():
        logger.info("Serving locally a preview of the built site")
        served_folder = os.path.realpath("build")
        if not os.path.isdir(served_folder):
            logger.warning("We miss the build folder in %s" % served_folder)
            logger.warning(
                "You'll need to flat.py init --template empty to create a base"
            )
            logger.warning(
                "And then run flat.py to collect data and update the template"
            )
            sys.exit(1)
        serve(served_folder)

    def init(self, template_name, build_folder="build"):
        logger.info("Initializing build folder with %s template" % template_name)
        builder = Builder()
        template_folder = os.path.join(TEMPLATE_CONTAINER_FOLDER, template_name)
        builder.init(template_folder)

    def list_templates(self):
        print("Available templates:")
        for name in os.listdir(TEMPLATE_CONTAINER_FOLDER):
            if name[0] in (".", "_"):
                continue  # Ignore hidden/temp folders
            template_folder = os.path.join(TEMPLATE_CONTAINER_FOLDER, name)
            if os.path.isdir(template_folder):
                try:
                    template = Template(template_folder)
                except NotATemplateFolder:
                    pass
                else:
                    description = template.config["description"]
                    print("\t{folder} - {desc}".format(folder=name, desc=description))
        print()

    def runapi(self, production=False, port=3001):
        from api.api_server import run_api

        run_api(self.db, production=production, port=port)

    def send_push_notifications(self, data):
        from push.send import broadcast_notification

        broadcast_notification(data, self.db)

    def send_push_history(self):
        """Send the notifications that clients are missing"""
        from push.send import send_all_missing_notifications

        send_all_missing_notifications(self.db)


def get_options():
    parser = argparse.ArgumentParser(
        "FlatDario",
        description="Aggregate your social activities in a simple fast static flat site",
    )
    parser.add_argument("-v", "--version", action="version", version=VERSION)
    parser.add_argument(
        "--debug",
        help="Run in debug mode, verbose output is shown",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--update",
        help="Scan all the elements and update them instead"
        " of doing an incremental sync",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "action",
        default="collect+build",
        nargs="?",
        choices=(
            "init",
            "collect+build",
            "collect",
            "build",
            "preview",
            "runapi",
            "notify",
        ),
        help=textwrap.dedent("""
                            init:    initialize the build/ folder with the template specified
                                     by the --template option (do --list to list templates)
                            collect: get the data from the sources and store in the local DB
                            build:   using the local DB update the content of build/
                            preview: serve the content of build/ to preview the result site
                            notify:  send the push notifications to subscribed clients 
                        """),
    )

    parser.add_argument(
        "--template",
        default="empty",
        help="Select the template to be used for build and preview",
    )

    parser.add_argument(
        "--list",
        help="List all the available templates",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--port",
        help="Serve the API and the Dynamic server on a given port",
        type=int,
        default=3001,
    )

    return parser.parse_args()


if __name__ == "__main__":
    print("FlatDario %s" % VERSION)
    this_year = datetime.date.today().year
    start_year = 2016
    copy_years = (
        start_year if this_year == start_year else "%s-%s" % (start_year, this_year)
    )
    print("Copyright (C) %s Dario Varotto\n" % copy_years)

    args = get_options()

    # configure logging level
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    agg = Aggregator()
    action = args.action
    if args.list:
        agg.list_templates()
        action = None
    if action in ("collect+build", "collect"):
        agg.collect(
            refresh_duplicates=args.update,
        )
        agg.send_push_history()  # notify after collection

    if action in ("collect+build", "build"):
        agg.build()

    if action == "init":
        agg.init(template_name=args.template)

    if action == "preview":
        agg.preview()

    if action == "runapi":
        if not args.debug and not single():
            # in debug mode, we have the watcher that run the 2nd time
            print("Process already runing")
            sys.exit()
        agg.runapi(production=not args.debug, port=args.port)

    if action == "notify":
        agg.send_push_history()
