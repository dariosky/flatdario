import logging

import opengraph

from flat import Aggregator

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


def fill_missing_infos(db):
    changes = 0
    for item in db.all():
        changed = False
        thumb = get_thumbnail(item)
        if not thumb:
            url = item['url']
            logger.warning(f"{item['type']} {item['title']} - parsing {url}")
            try:
                ogdata = opengraph.OpenGraph(url, scrape=True)
            except:
                ogdata = None
            if ogdata:
                ogtitle = f"{ogdata.get('site_name')}: " if ogdata.get('site_name') else ""
                ogtitle += ogdata.get('title')
                if ogtitle and ogtitle != item['title']:
                    logger.debug(f"Changed title {item['title']} => {ogtitle}")
                    item['title'] = ogtitle
                    changed = True
                if ogdata['image']:
                    item['thumb'] = ogdata['image']
                    changed = True
        else:
            if 'thumb' not in item:
                # adding the thumb in a single place
                item['thumb'] = thumb
                changed = True
        if changed:
            db.upsert(item, update=True)
            changes += 1
    logger.info(f"Changes: {changes}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    agg = Aggregator()
    fill_missing_infos(agg.db)
