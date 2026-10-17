"""Normalize SpaceX launches and add dates, counts, and outcome labels."""

from datetime import datetime, timezone


def _parse_utc(dt_str):
    """
    SpaceX date_utc looks like: '2020-05-30T19:22:00.000Z'
    Convert it to a timezone-aware datetime in UTC.
    """
    if not dt_str:
        return None
    try:
        # Replace trailing Z with +00:00 so fromisoformat can parse it
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def transform_spacex_launches(raw_payload):
    """
    Receives the extractor payload:
      {
        "metadata": {...},
        "data": [ {launch doc}, ... ]
      }

    Required transformations included:
      1) Clean/standardize a field: name normalized (trim + collapse whitespace)
      2) New calculated field(s): days_since_launch, payload_count, core_count, success_label
      3) Metadata: processed_at + source

    Returns: list[dict] ready to load into MongoDB.
    """
    if not raw_payload or "data" not in raw_payload:
        print("  [TRANSFORM_SPACEX] No data to transform")
        return []

    source = raw_payload.get("metadata", {}).get("source", "spacex-api/v4/launches/query")
    processed_at = datetime.utcnow().isoformat()

    transformed = []
    now_utc = datetime.now(timezone.utc)

    for launch in raw_payload["data"]:
        # SpaceX v4 typically provides "id". If it's missing due to select, fall back.
        date_utc_str = launch.get("date_utc")
        flight_number = launch.get("flight_number")

        launch_id = launch.get("id")
        if not launch_id:
            # Fallback unique-ish key if id wasn't included in extract
            launch_id = f"{flight_number}-{date_utc_str}"

        # 1) Clean / standardize
        name_raw = launch.get("name") or ""
        name_clean = " ".join(name_raw.strip().split())

        # Parse date
        dt = _parse_utc(date_utc_str)
        launch_date = dt.date().isoformat() if dt else None
        launch_year = dt.year if dt else None
        launch_month = f"{dt.year}-{dt.month:02d}" if dt else None

        # 2) Calculated fields
        cores = launch.get("cores") or []
        payloads = launch.get("payloads") or []
        core_count = len(cores)
        payload_count = len(payloads)

        success = launch.get("success")  # can be True/False/None
        upcoming = bool(launch.get("upcoming", False))

        if upcoming:
            success_label = "upcoming"
        elif success is True:
            success_label = "success"
        elif success is False:
            success_label = "failure"
        else:
            success_label = "unknown"

        days_since_launch = None
        if dt and dt <= now_utc:
            days_since_launch = (now_utc - dt).days

        # Some useful flattened fields
        links = launch.get("links") or {}
        patch = links.get("patch") or {}
        flickr = links.get("flickr") or {}

        details = (launch.get("details") or "").strip()
        details = " ".join(details.split())

        transformed_doc = {
            # Unique key for upsert
            "launch_id": launch_id,

            # Core attributes
            "name": name_clean,
            "flight_number": flight_number,
            "date_utc": date_utc_str,
            "launch_date": launch_date,
            "launch_year": launch_year,
            "launch_month": launch_month,
            "upcoming": upcoming,
            "success": success,
            "success_label": success_label,

            # References (IDs)
            "rocket_id": launch.get("rocket"),
            "launchpad_id": launch.get("launchpad"),
            "payload_ids": payloads,

            # Counts (calculated)
            "core_count": core_count,
            "payload_count": payload_count,
            "days_since_launch": days_since_launch,

            # Text / extras
            "details": details,

            # Links (flatten)
            "webcast": links.get("webcast"),
            "article": links.get("article"),
            "wikipedia": links.get("wikipedia"),
            "youtube_id": links.get("youtube_id"),
            "patch_small": patch.get("small"),
            "patch_large": patch.get("large"),
            "flickr_images_count": len(flickr.get("original") or []),

            # 3) Metadata required
            "processed_at": processed_at,
            "source": source,
        }

        transformed.append(transformed_doc)

    print(f"  [TRANSFORM_SPACEX] Transformed records: {len(transformed)}")
    return transformed


# Local check for this module. The full pipeline runs from main.py.
if __name__ == "__main__":
    sample = {
        "metadata": {"source": "spacex-api/v4/launches/query"},
        "data": [
            {
                "id": "abc123",
                "name": "  Starlink   4-1 ",
                "date_utc": "2022-01-19T02:00:00.000Z",
                "success": True,
                "rocket": "rocketid",
                "flight_number": 160,
                "upcoming": False,
                "details": "  test   details ",
                "cores": [{"core": "x"}, {"core": "y"}],
                "payloads": ["p1", "p2", "p3"],
                "launchpad": "lp1",
                "links": {"webcast": "x", "patch": {"small": "s", "large": "l"}, "flickr": {"original": []}},
            }
        ],
    }
    out = transform_spacex_launches(sample)
    print(out[0]["name"], out[0]["payload_count"], out[0]["success_label"])