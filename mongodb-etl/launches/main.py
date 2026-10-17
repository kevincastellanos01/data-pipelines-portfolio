"""Orchestrate the SpaceX launches pipeline across two API pages."""

import time

from extract import extract_spacex_launches
from transform import transform_spacex_launches
from load import load_spacex_launches


def run_spacex_etl(pages=2, limit=25):
    """Run the SpaceX pipeline for the given number of pages."""
    print("=" * 60)
    print("   SPACEX LAUNCHES — ETL Pipeline")
    print("=" * 60)

    pipeline_start = time.time()
    total_extracted = 0
    total_loaded = 0
    batches_processed = 0

    print(f"   Endpoint   : /v4/launches/query")
    print(f"   Batches    : {pages} (pages 1..{pages})")
    print(f"   Page size  : {limit}")
    print("=" * 60)

    for page in range(1, pages + 1):
        print(f"\n{'─' * 60}")
        print(f"   BATCH {page}/{pages}  |  page={page}")
        print(f"{'─' * 60}")

        batch_start = time.time()

        # EXTRACT
        raw = extract_spacex_launches(page=page, limit=limit, delay_seconds=1.0)
        if raw is None:
            print("  [PIPELINE_SPACEX] Skipping batch (extract returned None)")
            continue

        extracted_count = raw.get("metadata", {}).get("count", 0)
        total_extracted += extracted_count
        print(f"  [EXTRACT_SPACEX] Extracted: {extracted_count}")

        # TRANSFORM
        transformed = transform_spacex_launches(raw)
        if not transformed:
            print("  [PIPELINE_SPACEX] Skipping batch (no transformed records)")
            continue

        # LOAD
        loaded = load_spacex_launches(transformed)
        total_loaded += loaded
        batches_processed += 1

        batch_time = time.time() - batch_start
        print(f"  [PIPELINE_SPACEX] Batch done in {batch_time:.2f}s")

    total_time = time.time() - pipeline_start

    print(f"\n{'=' * 60}")
    print("   PIPELINE COMPLETE")
    print(f"{'=' * 60}")
    print(f"   Launches extracted : {total_extracted}")
    print(f"   Launches loaded    : {total_loaded}")
    print(f"   Batches processed  : {batches_processed}/{pages}")
    print(f"   Total time         : {total_time:.2f}s")
    print(f"{'=' * 60}")
    print("   View your data in Mongo Express:")
    print("   http://localhost:8081")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    run_spacex_etl(pages=2, limit=25)