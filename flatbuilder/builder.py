import logging
import os

import yaml

from .util import recursive_overwrite

logger = logging.getLogger(__name__)

CONFIG_FILENAME = 'buildconfig.yaml'


class Builder():
    def run(self, items, folder):
        """ Given an iterable of items generate the flat static site """
        logger.info("Generating the flat site in %s" % folder)
        try:
            template = Template(folder)
        except NotATemplateFolder:
            logger.error(
                "Build folder doesn't seem coming from a template, we need %s" % CONFIG_FILENAME
            )
            return
        print(template.config)

    def init(self, template_folder, build_folder='build'):
        template_name = os.path.basename(template_folder)
        if os.path.isdir(build_folder):
            logger.warning("Build folder already exists.")
            response = input("Do you want to copy the template %s over"
                             " (files with same name will be overwritten) [y/N]? " % template_name, )
            if response.lower() != 'y':
                logger.info("We don't overwrite, exiting.")
                return 1
        try:
            template = Template(template_folder)
        except (NotATemplateFolder, FileNotFoundError):
            logger.error("Invalid template %s" % template_name)
            return 1
        else:
            logger.info("Copying template %s to build folder" % template)
            recursive_overwrite(template_folder, build_folder)


class NotATemplateFolder(Exception):
    pass


class Template():
    def __init__(self, folder):
        config_file = os.path.join(folder, CONFIG_FILENAME)
        self.name = os.path.basename(folder)
        if not os.path.isfile(config_file):
            raise NotATemplateFolder()
        self.config = yaml.load(open(config_file))

    def __str__(self):
        return self.name
