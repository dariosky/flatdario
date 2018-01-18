#!/usr/bin/env python
import argparse
import datetime
import json
import logging
import os
import sys
import textwrap

from collectors import *
from flatbuilder.builder import Builder, Template, NotATemplateFolder
from flatbuilder.preview import serve
from storage import Storage

logger = logging.getLogger(__name__)
VERSION = "0.2"
TEMPLATE_CONTAINER_FOLDER = "flatbuilder"


class Aggregator:
    collectors = [
        YouTubeLikesCollector,
        PocketCollector,
        VimeoCollector,
    ]

    def __init__(self):
        super(Aggregator, self).__init__()
        config = self.load_config()
        c = config.get
        self.db_filename = c('db', 'db.json')
        self.db_format = c('format', 'json')
        self.build_template = c('template', 'empty')

        self.db = Storage.get(self.db_format, self.db_filename)

    @staticmethod
    def load_config(config_file='flat.json'):
        if os.path.isfile(config_file):
            logger.debug(f"Getting configuration from {config_file}")
            with open(config_file, 'r', encoding='utf8') as f:
                return json.load(f)
        return {}

    def save_item(self, item, update=False):
        self.db.upsert(item, update)  # insert/update and raise if exists

    def collect(self, refresh_duplicates=False):
        logger.info("Running the Collectors")
        for collector_class in self.collectors:
            logger.info(collector_class.__name__)
            collector = collector_class()
            # we can decide the initial collect parameter looking at the DB?
            initial_collect_params = collector.initial_parameters(
                self.db,
                refresh_duplicates=refresh_duplicates
            )
            # Run the collector
            collector.run(callback=self.save_item,
                          refresh_duplicates=refresh_duplicates,
                          **initial_collect_params)

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
        served_folder = os.path.realpath('build')
        if not os.path.isdir(served_folder):
            logger.warning("We miss the build folder in %s" % served_folder)
            logger.warning("You'll need to flat.py init --template empty to create a base")
            logger.warning("And then run flat.py to collect data and update the template")
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
            if name[0] in ('.', '_'):
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


def get_options():
    parser = argparse.ArgumentParser(
        "FlatDario",
        description="Aggregate your social activities in a simple fast static flat site"
    )
    parser.add_argument("-v", "--version", action="version", version=VERSION)
    parser.add_argument("--debug",
                        help="Run in debug mode, verbose output is shown",
                        default=False,
                        action="store_true")
    parser.add_argument("--update",
                        help="Scan all the elements and update them instead"
                             " of doing an incremental sync",
                        default=False,
                        action="store_true")

    parser.add_argument('action',
                        default="collect+build", nargs='?',
                        choices="init, collect+build, collect, build, preview".split(", "),
                        help=textwrap.dedent("""
                            init:    initialize the build/ folder with the template specified
                                     by the --template option (do --list to list templates)
                            collect: get the data from the sources and store in the local DB
                            build:   using the local DB update the content of build/
                            preview: serve the content of build/ to preview the result site
                        """),
                        )

    parser.add_argument("--template",
                        default='empty',
                        help="Select the template to be used for build and preview",
                        )

    parser.add_argument("--list",
                        help="List all the available templates",
                        default=False,
                        action="store_true")

    return parser.parse_args()


if __name__ == '__main__':
    print("FlatDario %s" % VERSION)
    this_year = datetime.date.today().year
    start_year = 2016
    copy_years = start_year if this_year == start_year else "%s-%s" % (start_year, this_year)
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
            refresh_duplicates=args.update
        )

    if action in ("collect+build", "build"):
        agg.build()

    if action == "init":
        agg.init(template_name=args.template)

    if action == "preview":
        agg.preview()
