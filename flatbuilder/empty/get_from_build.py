"""This script clear the dynamic things from the build path
and place them back in the template...
Useful to commit any new customization, without publishing your data
"""

import logging
import os

from flatbuilder.builder import Builder
from flatbuilder.util import recursive_overwrite

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("template.frombuild")
if __name__ == "__main__":
    logger.info("Clearing the build folder")
    builder = Builder()
    build_folder = "build"
    builder.run(items=[], folder=build_folder)
    template_folder = os.path.dirname(__file__)
    logger.info("Copy back to this template folder: %s" % template_folder)
    recursive_overwrite(src=build_folder, dest=template_folder)
