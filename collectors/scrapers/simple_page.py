import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from api.util.compat import patch_collections_for_py3

logger = logging.getLogger(__name__)
patch_collections_for_py3()


def get_best_image(url):
    """Try to get a reasonable image without JS rendering."""
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "flatdario"})
        if response.status_code != 200:
            return None
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
    if og and og.get("content"):
        return urljoin(url, og["content"])
    tw = soup.find("meta", property="twitter:image") or soup.find(
        "meta", attrs={"name": "twitter:image"}
    )
    if tw and tw.get("content"):
        return urljoin(url, tw["content"])

    best = None
    best_area = 0
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        try:
            width = int(img.get("width", 0))
            height = int(img.get("height", 0))
            area = width * height
        except ValueError:
            area = 0
        if area > best_area:
            best_area = area
            best = src

    if not best:
        first = soup.find("img")
        if first and first.get("src"):
            best = first.get("src")

    return urljoin(url, best) if best else None


def get_page_title(url):
    """Return the HTML <title> as a fallback."""
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "flatdario"})
        if response.status_code != 200:
            return None
    except Exception as exc:
        logger.warning("Failed to fetch title for %s: %s", url, exc)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        return title or None
    return None
