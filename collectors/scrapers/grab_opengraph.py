import logging

import opengraph

from collectors.scrapers.render_page import grab_largest_image

logger = logging.getLogger(__name__)


def get_thumbnail(item):
    itype = item['type']
    if 'thumb' in item:
        return item['thumb']
    try:
        if itype == 'Youtube':
            return item['thumbnails']['medium']['url']
        elif itype == 'Pocket':
            return item['images'][0]
        elif itype == 'Vimeo':
            return item['thumbnails']['sizes'][2]['link']
        elif itype == 'RSS':
            return item['thumbnail']
        elif itype == 'Tumblr':
            return item['img']
        else:
            logger.warning(f"Can't get thumbnail for {itype}")
    except (KeyError, AttributeError, IndexError):
        pass


def get_thumb_from_opengraph(item):
    changed = False
    url = item['url']
    logger.info(f"{item['type']} {item['title']} - parsing {url}")
    try:
        ogdata = opengraph.OpenGraph(url, scrape=True)
    except:
        ogdata = None
    if ogdata:
        # we have the parsed data, let's also update the title
        ogtitle = f"{ogdata.get('site_name')}: " if ogdata.get('site_name') else ""
        ogtitle += ogdata.get('title')
        if ogtitle and ogtitle != item['title']:
            logger.debug(f"Changed title {item['title']} => {ogtitle}")
            item['title'] = ogtitle.strip()
            changed = True
        if ogdata['image']:
            thumb = ogdata['image']
            if not thumb.startswith("/"):  # ignore relative images
                item['thumb'] = thumb  # do the change
                changed = True
    return changed


def fill_missing_infos(db, items=None):
    logger.debug('Filling missing infos')
    changes = 0
    for item in items or db.all():
        if item.get('thumb'):  # temp
            continue
        changed = False

        if not item.get('thumb'):
            # get from content
            content_thumb = get_thumbnail(item)
            if content_thumb:
                item['thumb'] = content_thumb
                changed = True

        if not item.get('thumb'):
            # parse the site to get a thumbnail
            changed = changed or get_thumb_from_opengraph(item)

        if not item.get('thumb'):
            # parse and grab the biggest image
            thumb = grab_largest_image(item['url'])
            if thumb:
                logger.info(f"Using largest image: {thumb}")
                item['thumb'] = thumb
                changed = True

        if not item.get('thumb'):
            item['thumb'] = ''  # stop searching for thumbs
            changed = True

        if changed:
            db.upsert(item, update=True)
            changes += 1
            # stop searching for thumb

    logger.info(f"Changes: {changes}")


if __name__ == '__main__':
    from flat import Aggregator

    logging.basicConfig(level=logging.INFO)
    agg = Aggregator()
    fill_missing_infos(agg.db)
