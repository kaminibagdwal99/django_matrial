import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_rank_using_google_cse(keyword, target_domain, region="Global", max_results=100):
    """Fetch website rank using Google Custom Search API."""
    cse_id = settings.CSE_IDS.get(region, settings.CSE_IDS["Global"])
    api_key = settings.GOOGLE_API_KEY

    for start_index in range(1, max_results, 10):
        params = {
            "q": keyword,
            "key": api_key,
            "cx": cse_id,
            "num": 10,
            "start": start_index
        }

        try:
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
            results = response.json()

            if "items" in results:
                for idx, item in enumerate(results["items"], start=start_index):
                    if target_domain in item["link"]:
                        return idx
        except Exception as e:
            logger.error(f"[Google CSE] Error for keyword '{keyword}': {e}")
            return None

    return None  # Not in top N

def get_ranks_for_multiple_keywords(keywords, target_domain, region="Global"):
    """Fetch website ranks for multiple keywords."""
    return {
        keyword: get_rank_using_google_cse(keyword, target_domain, region)
        for keyword in keywords
    }
