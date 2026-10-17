"""Fetch one page of SpaceX launches from the v4 query API."""

import time
import requests
from datetime import datetime

SPACEX_QUERY_URL = "https://api.spacexdata.com/v4/launches/query"


def extract_spacex_launches(page=1, limit=25, delay_seconds=1.0, timeout=15):
    """
    Fetch ONE batch (page) of SpaceX launches using the official v4 /launches/query endpoint.

    Call this once per page. main.py requests two pages by default.

    Returns:
      {
        "metadata": {...},
        "data": [ {launch doc}, ... ],
        "raw":  {full API response}
      }
    or None if the request fails.
    """
    try:
        payload = {
            # You can add filters here if you want smaller datasets.
            # Example: only launches from 2020+:
            # "query": {"date_utc": {"$gte": "2020-01-01T00:00:00.000Z"}},
            "query": {},
            "options": {
                "page": page,
                "limit": limit,
                "sort": {"date_utc": "desc"},
                # Selecting fewer fields makes the request faster / lighter.
                "select": {
                    "name": 1,
                    "date_utc": 1,
                    "success": 1,
                    "rocket": 1,
                    "flight_number": 1,
                    "upcoming": 1,
                    "details": 1,
                    "cores": 1,
                    "payloads": 1,
                    "launchpad": 1,
                    "links": 1,
                },
            },
        }

        print(f"  [EXTRACT_SPACEX] POST {SPACEX_QUERY_URL} | page={page} limit={limit}")
        resp = requests.post(SPACEX_QUERY_URL, json=payload, timeout=timeout)
        resp.raise_for_status()

        raw = resp.json()
        docs = raw.get("docs", [])

        # Small delay to be respectful + match assignment requirement
        time.sleep(delay_seconds)

        return {
            "metadata": {
                "source": "spacex-api/v4/launches/query",
                "fetched_at": datetime.utcnow().isoformat(),
                "page": page,
                "limit": limit,
                "count": len(docs),
                "totalDocs": raw.get("totalDocs"),
                "totalPages": raw.get("totalPages"),
                "hasNextPage": raw.get("hasNextPage"),
                "hasPrevPage": raw.get("hasPrevPage"),
                "nextPage": raw.get("nextPage"),
                "prevPage": raw.get("prevPage"),
            },
            "data": docs,
            "raw": raw,
        }

    except requests.RequestException as e:
        print(f"  [EXTRACT_SPACEX] ERROR: {e}")
        return None


# Optional quick test (doesn't replace main_spacex.py)
if __name__ == "__main__":
    batch1 = extract_spacex_launches(page=1, limit=5)
    batch2 = extract_spacex_launches(page=2, limit=5)
    print("Batch1 count:", 0 if not batch1 else batch1["metadata"]["count"])
    print("Batch2 count:", 0 if not batch2 else batch2["metadata"]["count"])