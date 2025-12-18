import logging

logger = logging.getLogger(__name__)


def grab_largest_image(url):
    import asyncio
    from pyppeteer import launch

    async def main():
        browser = None
        try:
            browser = await launch()
            page = await browser.newPage()
            logger.info(f"Opening page {url}")

            await page.goto(url, timeout=10000)

            max_img = await page.evaluate("""() => {
                        var images = document.getElementsByTagName('img')
                        var maxImg = null, maxArea=0, anchor;
                        for (var i=0, len=images.length; i<len; i++)  {
                            img = images[i];
                            var imgArea = img.naturalWidth * img.naturalHeight;
                            if (imgArea > maxArea) {
                                maxArea = imgArea;
                                maxImg = img.src
                            }
                        }
                        if (maxImg) {
                            anchor = document.createElement('a');
                            anchor.href = maxImg;
                            return anchor.href; // return the absolute path
                        }
                        return maxImg
                    }""")
            return max_img
        except Exception as e:
            logger.error(f"Error rendering page {url}")
            pass
        finally:
            if browser:
                await browser.close()

    return asyncio.get_event_loop().run_until_complete(main())
