import logging
import requests
from playwright.sync_api import sync_playwright


def get_embed_code(tweet_url: str) -> str:
    response = requests.get("https://publish.twitter.com/oembed", params={
        "url": tweet_url
    })

    if response.ok:
        return response.json()

    return None


def take_screenshot(html_file: str, screenshot_file: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(html_file)

        iframe = page.locator("#twitter-widget-0")
        
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(2000)

        iframe.screenshot(path=screenshot_file)

        page.close()
        browser.close()


def get_tweet_id(tweet_url: str) -> str:
    from urllib.parse import urlparse
    parsed_data = urlparse(tweet_url)
    if parsed_data.path:
        exploded_path = parsed_data.path.split("/status/")
        return exploded_path[1]
    return None
    
def capture(tweet_url: str) -> bool:
    pass

if __name__ == "__main__":
    import os
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"
    )

    if len(sys.argv) <= 1:
        logging.error("Please input tweet URL as first argument.")
        sys.exit(0)

    tweet_url = sys.argv[1]
    tweet_id = get_tweet_id(tweet_url=tweet_url)
    
    if tweet_id is not None:
        html_file = os.path.abspath(f"html/{tweet_id}.html")
        screenshot_file = os.path.abspath(f"screenshots/{tweet_id}.png")

        logging.info("Start download embed code.")

        embed_code = get_embed_code(tweet_url=tweet_url)
        
        logging.info("Downloaded embed code.")

        with open(html_file, "w") as f:
            f.write(embed_code.get("html"))

        logging.info("Start browser to render embed code as HTML.")
        
        take_screenshot(html_file=f"file://{html_file}", screenshot_file=screenshot_file)

        logging.info(f"Embed: {html_file}")
        logging.info(f"Image: {screenshot_file}")
