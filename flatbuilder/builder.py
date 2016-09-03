import logging
import os

import yaml
from pyquery import PyQuery

from .util import recursive_overwrite

logger = logging.getLogger(__name__)

CONFIG_FILENAME = 'buildconfig.yaml'


class Builder():
    def __init__(self, build_folder='build'):
        self.build_folder = build_folder

    def init(self, template_folder):
        template_name = os.path.basename(template_folder)
        if os.path.isdir(self.build_folder):
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
            recursive_overwrite(template_folder, self.build_folder)

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

        template.process(items, folder=self.build_folder)


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

    def process(self, items, folder):
        """ Parse the pages of the template and do the dynamic substitutions in folder """
        for page in self.config['pages']:
            path = page['path'].lstrip("/")  # strip absolute path, we are relative to build
            if not path or path.endswith("/"):
                path += "index.html"
            print("Processing page", page, path)
            file_path = os.path.join(folder, path)
            selector = page['blockSelector']
            if not os.path.isfile(file_path):
                logger.debug(
                    "File missing [%s] creating an empty one with just the placeholder." % path)
                file_folder = os.path.dirname(file_path)
                if not os.path.exists(file_folder):
                    os.makedirs(file_folder, exist_ok=True)
                with open(file_path, "w") as f:
                    assert selector[0] in ('.', '#'), "I was expecting a class or id selector"
                    selector_name = "id" if selector[0] == "#" else "class"
                    selector_value = selector[1:]
                    f.write("<html><body><div {attr}='{value}'></div></body></html>".format(
                        attr=selector_name, value=selector_value
                    ))
            with open(file_path, "r") as f:
                c = PyQuery(f.read())
                old_content = str(c(selector))
                print(old_content)

            c(selector).html("Generated content, should come from a template")
            new_content = str(c(selector))
            if old_content != new_content:
                print("I should save back")
                with open(file_path, "w") as f:
                    f.write(str(c))
