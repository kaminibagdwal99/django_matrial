import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

GOOGLE_API_KEY = 'AIzaSyCuAT-t8xAMGvV7vHbAjD68CMvV9fX0-MQ'
CSE_IDS = {
    'Global': '46a536f3718f04ce0',
    'Singapore': '1504d800b0041483c',
    'Thailand': '21e861831915645c2',
}
def get_rank_using_google_cse(keyword, target_domain, region="Global", max_results=100):
    """Use Google CSE to get keyword ranking (safe method)."""
    cse_id = CSE_IDS.get(region, CSE_IDS["Global"])
    api_key = GOOGLE_API_KEY

    parsed_target = urlparse(target_domain).netloc.replace("www.", "")

    for start_index in range(1, max_results, 10):
        params = {
            "q": keyword,
            "key": api_key,
            "cx": cse_id,
            "num": 10,
            "start": start_index
        }
        try:
            res = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
            items = res.json().get("items", [])
            for idx, item in enumerate(items, start=start_index):
                if parsed_target in urlparse(item['link']).netloc:
                    return idx
        except Exception as e:
            logger.error(f"[CSE Error] {keyword}: {e}")
            return None
    return None


from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

def get_rank_with_playwright(keyword, target_domain, region="us", max_pages=5):
    parsed_target = urlparse(target_domain).netloc.replace("www.", "")
    rank = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for page_num in range(max_pages):
            start = page_num * 10
            search_url = f"https://www.google.com/search?q={keyword}&start={start}&gl={region}&hl=en"

            print(f"🌐 Visiting: {search_url}")
            page.goto(search_url, timeout=60000)
            page.wait_for_timeout(2000)  # wait for results to load

            results = page.locator('div.yuRUbf > a')
            count = results.count()

            for i in range(count):
                link = results.nth(i).get_attribute("href")
                if not link:
                    continue
                parsed_link = urlparse(link).netloc.replace("www.", "")
                print(f"🔗 {start+i+1}: {parsed_link} - {link}")
                if parsed_target in parsed_link:
                    rank = start + i + 1
                    print("✅ Match found!")
                    browser.close()
                    return rank

        browser.close()
    return None


def get_rank(keyword, target_domain, region="Global"):
    """Try Google CSE first, then fallback to scraping."""
    rank = get_rank_using_google_cse(keyword, target_domain, region)
    if rank is not None:
        return {"rank": rank, "source": "cse"}

    rank = get_rank_with_playwright(keyword, target_domain, region)
    if rank is not None:
        return {"rank": rank, "source": "scraper"}

    return {"rank": None, "source": "none"}


rank = get_rank_with_playwright(
    keyword="pigmentation removal singapore",
    target_domain="https://www.limclinicandsurgery.com/",
    region="sg",  # use ISO 2-letter code
    max_pages=10
)
print("Rank:", rank)

