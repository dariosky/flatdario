from collectors.scrapers.render_page import grab_largest_image


def test_grab_largest():
    thumb = grab_largest_image("https://xkcd.com/1998/")
    assert thumb == "https://imgs.xkcd.com/comics/gdpr.png"
