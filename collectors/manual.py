import datetime
import hashlib
import logging
import re
from urllib.parse import urlparse, parse_qs

import requests

from collectors.scrapers.grab_opengraph import get_thumb_from_opengraph
from collectors.scrapers.simple_page import get_best_image, get_page_title

from api.util.compat import patch_collections_for_py3

logger = logging.getLogger(__name__)
patch_collections_for_py3()


YOUTUBE_DOMAINS = ("youtube.com", "www.youtube.com", "youtu.be")


def _hash_id(value):
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def _is_youtube(url):
    host = urlparse(url).netloc.lower()
    return any(host == d for d in YOUTUBE_DOMAINS)


def _extract_youtube_id(url):
    parsed = urlparse(url)
    if parsed.netloc.lower() == "youtu.be":
        return parsed.path.lstrip("/")
    qs = parse_qs(parsed.query)
    if "v" in qs:
        return qs["v"][0]
    match = re.search(r"/embed/([A-Za-z0-9_-]+)", parsed.path)
    if match:
        return match.group(1)
    return None


def _youtube_oembed(url):
    endpoint = "https://www.youtube.com/oembed"
    response = requests.get(endpoint, params={"url": url, "format": "json"}, timeout=10)
    if response.status_code != 200:
        raise Exception("Failed to fetch YouTube metadata")
    return response.json()


def build_item_from_url(url):
    """Build a minimal item dict from a URL."""
    if _is_youtube(url):
        video_id = _extract_youtube_id(url) or _hash_id(url)
        data = _youtube_oembed(url)
        return {
            "id": video_id,
            "type": "Youtube",
            "subtype": "manual",
            "url": url,
            "timestamp": datetime.datetime.utcnow(),
            "title": data.get("title") or url,
            "thumb": data.get("thumbnail_url"),
            "provider_name": data.get("provider_name"),
        }

    # Generic URL fallback
    item = {
        "id": _hash_id(url),
        "type": "Manual",
        "subtype": "manual",
        "url": url,
        "timestamp": datetime.datetime.utcnow(),
        "title": url,
    }
    if not item.get("title") or item["title"] == url:
        title = get_page_title(url)
        if title:
            item["title"] = title
    try:
        get_thumb_from_opengraph(item)
    except Exception as exc:
        logger.warning("OpenGraph failed for %s: %s", url, exc)
    if not item.get("thumb"):
        try:
            item["thumb"] = get_best_image(url) or ""
        except Exception as exc:
            logger.warning("Image parse failed for %s: %s", url, exc)
            item["thumb"] = ""
    return item
