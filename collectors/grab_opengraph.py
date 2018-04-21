import logging

import opengraph

logger = logging.getLogger(__name__)
logging.getLogger('chardet').setLevel(logging.INFO)


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


def fill_missing_infos(db, items=None):
    logger.debug('Filling missing infos')
    changes = 0
    for item in items or db.all():
        changed = False
        if 'thumb' not in item:
            thumb = get_thumbnail(item)
            if not thumb:
                # parse the site to get a thumbnail
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
                    if ogdata['image']:
                        thumb = ogdata['image']
            # in the end, we always set a thumb (eventually to None)
            item['thumb'] = thumb
            changed = True
        if changed:
            db.upsert(item, update=True)
            changes += 1
    logger.info(f"Changes: {changes}")


if __name__ == '__main__':
    from flat import Aggregator

    logging.basicConfig(level=logging.DEBUG)
    agg = Aggregator()
    fill_missing_infos(agg.db)
